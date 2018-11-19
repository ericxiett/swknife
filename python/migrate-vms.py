#!/usr/bin/python env
# -*- coding: utf-8 -*-

import re
import logging
import os
from xlrd import open_workbook
from novaclient import client
from keystoneauth1 import loading, session

LOGGER = None
MAX_COLUMNS = 2
COLUME_NAME = ["name", "tag"]
DEST = 'dest'


def setup_logging(debug=False):
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level)


def get_logger():
    global LOGGER
    if not LOGGER:
        LOGGER = logging.getLogger(__name__)
    return LOGGER


class Server(object):

    def __init__(self, name, host, tag, vcpu=0, ram=0, service=None, az=None):

        # this id will not be used if
        # search name returns a list with more than 1 element
        self.id = name
        self.name = name
        self.host = host
        self.vcpus = vcpu
        self.ram = ram
        self.tag = tag
        self.service = service if service else "ecs"
        self.az = az if az else "cn-north-3a"
        self.aggregate = "%s_%s_%s" % (self.az, self.service, "general")

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "%s_%s_%s_%s" % (self.id, self.aggregate, self.host, self.tag)

    def tag_vm(self, nova_client):
        """
        tag vm
        :param nova_client:
        :return:
        """

        logger = get_logger()
        # fixme vm name duplication?
        # instead it uses database style (mysql...)
        server = object()
        setattr(server, 'id', self.id)
        server = nova_client.servers.get(server)

        # quit if not tag provided
        if not self.tag:
            return

        # tag this vm
        tag_list = [i for i in nova_client.servers.tag_list(server)]
        if self.tag not in tag_list:
            logger.info('create tag %s for vm %s (%s)', self.tag, self.name, server.id)
            nova_client.servers.add_tag(server, self.tag)
        else:
            logger.info('vm: %s(%s) already has tag: %s', self.name, server.id, self.tag)

    @classmethod
    def create(cls, nova_client, name, tag):
        logger = get_logger()
        # fixme vm name duplication?
        # instead it uses database style (mysql...)
        servers = nova_client.servers.list(detailed=False, search_opts={"name": name, "all_tenants": True})

        if len(servers) == 0:
            # this trick utilizes the fact only id attribute is required for this get method
            a = Server(name, None, None)
            servers = [nova_client.servers.get(a)]

        if len(servers) == 0:
            # this method might be redundant, nova may support regex natively?
            # fixme Number of servers > default limit?
            logger.info('searching through all existing vms, this could be heavy')
            all_servers = nova_client.servers.list(detailed=False, search_opts={"all_tenants": True})
            for one in all_servers:
                if re.match(name, one.name):
                    servers.append(one)

        ret = []
        for server in servers:
            detailed_server = nova_client.servers.get(server)
            host = getattr(detailed_server, 'OS-EXT-SRV-ATTR:host')
            vcpus = detailed_server.flavor['vcpus']
            ram = detailed_server.flavor['ram']
            ret.append(Server(server.id, host, tag, vcpus, ram))

        return ret


class Host(object):

    def __init__(self, id, name, vcpus, ram, **kwargs):
        self.id = id
        self.name = name
        self.vcpus = vcpus
        self.ram = ram
        self.hypervisor_type = kwargs.get('hypervisor_type', "QEMU")

    def take_cpu(self, cpu):
        self.vcpus -= cpu

    def take_ram(self, ram):
        self.ram -= ram

    def assign_server(self, server):
        self.take_cpu(server.vcpu)
        self.take_ram(server.ram)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()

    def __lt__(self, other):
        if self.vcpus == other.vcpus:
            return other.ram < self.ram
        else:
            return other.vcpus < self.vcpus

    def __eq__(self, other):
        return self.name == other.name


class Aggregate(object):

    def __init__(self, name, hosts=list()):
        self.name = name
        self.hosts = hosts

    def add_host(self, host):
        self.hosts.append(host)


def assemble_aggregates(nova_client):
    """
    construct a aggregates map
    :param nova_client:
    :return:
    """
    hosts = {i.service['host']: Host(i.id, i.service['host'], i.vcpus, i.memory_mb)
             for i in nova_client.hypervisors.list()}
    aggregates = {i.name: Aggregate(i.name, [hosts.get(j) for j in i.hosts])
                  for i in nova_client.aggregates.list()}

    return aggregates


def update_host(host, vm):
    host.vcpus -= vm.vcpus
    host.ram -= vm.ram


def schedule_vms(aggregates, vms):
    """
    schedule vms
    :param aggregates:
    :param vms:
    :return: vms
    """

    logger = get_logger()

    for vm in vms:
        current_host = vm.host
        correct_aggregate = vm.aggregate
        if current_host not in [i.name for i in aggregates[correct_aggregate].hosts]:
            # compute dest and assign to vm
            hosts = aggregates[correct_aggregate].hosts
            index = sorted(range(len(hosts)), key=lambda i: hosts[i])[-1]
            logger.info("%s will be moved from %s to %s", vm.id, current_host, hosts[index])
            setattr(vm, DEST, hosts[index])
            update_host(hosts[index], vm)
            # todo should update current host as well?

    return vms


def read_config(nova_client, config_path):
    # fixme remore duplicate record and log
    if not os.path.exists(config_path):
        raise Exception("path: %s does not exist!", config_path)

    logger = get_logger()
    servers = []

    logger.info("read configuration from %s", config_path)
    wb = open_workbook(config_path)

    # by default, there is only a single sheet
    sheet = wb.sheets()[0]

    # ignore the first row
    for row in range(1, sheet.nrows):
        args = {
            "nova_client": nova_client
        }
        for col in range(sheet.ncols):

            # there should not be more than defined
            # number of columns
            if col > MAX_COLUMNS:
                break

            # fixme value might have letter like 'G'
            val = sheet.cell(row, col).value
            args[COLUME_NAME[col]] = val

        logger.info("args: %s", str(args))
        servers.extend(Server.create(**args))

    return servers


def tag_vm(nova_client, vms):
    """
    add tag to virtual machines
    :param nova_client:
    :param vms:
    :return:
    """

    logger = get_logger()
    for vm in vms:
        try:
            logger.info('start dealing with %s', vm.name)
            vm.tag_vm(nova_client)
        except Exception as e:
            logger.exception("add tag to vm: %s failed", str(vm))


def init_nova_client(credentials):
    # get logger
    logger = get_logger()

    # relation between variable name & corresponding environment variable
    required_fields = {'auth_url': 'OS_AUTH_URL',
                       'username': "OS_USERNAME",
                       'password': 'OS_PASSWORD',
                       'user_domain_name': "OS_USER_DOMAIN_NAME",
                       'project_name': "OS_PROJECT_NAME",
                       'project_domain_name': "OS_PROJECT_DOMAIN_NAME"
                       }

    # check & pop values from environment variable
    options = {}
    for key in required_fields.keys():
        if not credentials.get(key):
            value = os.environ[required_fields[key]]
            if not value:
                raise Exception("%s(%s) is missing" % (key, required_fields[key]))
            options.update({key: value})
        else:
            options.update({key: credentials.get(key)})

    logger.info("begin initializing nova client")
    loader = loading.get_plugin_loader('v3password')
    auth = loader.load_from_options(**options)
    sess = session.Session(auth=auth, verify=False)

    # fixme fix this ugle code!!
    endpoint_type = credentials.get('endpoint_type', os.environ['OS_ENDPOINT_TYPE'])
    endpoint_type = endpoint_type if endpoint_type else "public"
    region_name = credentials.get('region_name', os.environ['OS_REGION_NAME'])
    region_name = region_name if region_name else "RegionOne"

    nova_client = client.Client('2.53', session=sess, endpoint_type=endpoint_type, region_name=region_name)
    logger.info("initialzing nova client completed successfully")

    # return a glance client
    return nova_client


def get_all_servers(nova_client):
    all_servers = []

    last = None
    while True:
        servers = nova_client.servers.list(detailed=True, search_opts={"all_tenants": True},
                                           marker=last.id if last else None)
        if len(servers) == 0:
            break
        all_servers.extend(servers)
        last = all_servers[-1]
    return all_servers


def get_parser():
    import argparse

    parser = argparse.ArgumentParser(description='generate required flavors')
    parser.add_argument('-f', '--config', dest='config_path', required=True,
                        help='path to the configuration file')
    parser.add_argument('-d', '--debug', dest='debug', action='store_const', const=True,
                        default=False, help='enable debugging')

    return parser.parse_args()


def cmp(a, b):
    return a


def main():
    parser = get_parser()
    setup_logging(parser.debug)

    nova_client = init_nova_client({})
    logger = get_logger()

    servers = read_config(nova_client, parser.config_path)
    logger.info('%s', servers)
    aggregates = assemble_aggregates(nova_client)
    schedule_vms(aggregates, servers)


if __name__ == "__main__":
    exit(main())
