#!/usr/bin/python env
# -*- coding: utf-8 -*-

import logging
import os
import re
import time
from Queue import Queue

import xlwt
from keystoneauth1 import loading, session
from novaclient import client
from xlrd import open_workbook

DEFAULT_TIMEOUT = 10 * 60
WAITING_QUEUE_MAX_SIZE = 10
LOGGER = None
MAX_COLUMNS = 2
COLUME_NAME = ["name", "tag"]
DEST = 'dest'

LIVE_MIGRATIBLE_STATES = ['active', 'puased']
MIGRATIBLE_STATES = ['active', 'shutoff']
ERROR_STATE = ['error']
TRANSITIONAL_STATE = 'migrating'
COMPLETED_STATES = MIGRATIBLE_STATES + LIVE_MIGRATIBLE_STATES


def setup_logging(debug=False):
    logging_format = "%(asctime)s - %(name)10s.%(lineno)4s - %(levelname)5s - %(message)s"
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level, format=logging_format)


def get_logger():
    global LOGGER
    if not LOGGER:
        LOGGER = logging.getLogger(__name__)
    return LOGGER


class Server(object):
    available = "active"

    def __init__(self, server_id, name, host, tag, vcpu=0, ram=0, service=None, az=None):

        # this id will not be used if
        # search name returns a list with more than 1 element
        self.id = server_id
        self.name = name
        self.host = host
        self.vcpus = vcpu
        self.ram = ram
        self.tag = tag

        if service:
            self.service = service.strip()
        elif tag:
            self.service = tag.strip()
        else:
            self.service = ''

        self.az = az if az else "cn-north-3a"
        self.aggregate = "%s_%s_%s" % (self.az, self.service.lower(), "general")

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
        server = nova_client.servers.get(self)

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

    def could_migrate(self, server):
        if server.status.lower() in MIGRATIBLE_STATES:
            return True
        else:
            return False

    def could_live_migrate(self, server):
        if server.status.lower() in LIVE_MIGRATIBLE_STATES:
            return True
        else:
            return False

    def migrate(self, nova_client):

        server = nova_client.servers.get(self)
        logger = get_logger()

        if self.could_live_migrate(server):
            logger.debug("live migrate server %s", server)
            self.live_migrate(nova_client, False)
        elif self.could_migrate(server):
            logger.debug("cold migrate server %s", server)
            self.cold_migrate(nova_client)
        else:
            logger.info("server %s is not in active/stopped state, cannot live migrate it", self.id)
            raise ServerErrorStateException('server in non migrable state')

    def cold_migrate(self, nova_client):
        server = nova_client.servers.get(self)

        try:
            nova_client.servers.migrate(server)

            tic = time.time()

            while time.time() - tic < DEFAULT_TIMEOUT:
                server = nova_client.servers.get(self)
                if server.status == 'resize_confirm':
                    server.confirm_resize()
                time.sleep(10)
            else:
                raise ColdMigrationFailedException('cold migration of %s timeout' % server)

        except Exception:
            raise ColdMigrationFailedException('cold migration of %s failed' % server)

    def live_migrate(self, nova_client, block=False):
        dest = getattr(self, DEST)
        server = nova_client.servers.get(self)
        logger = get_logger()

        if not self.could_live_migrate(server):
            logger.info("server %s is not in active/stopped state, cannot live migrate it", self.id)
            raise ServerErrorStateException('server in non migrable state')

        nova_client.servers.live_migrate(server, dest, False, True)

        if block:
            tic = time.time()
            while True:
                toc = time.time()

                if toc - tic > DEFAULT_TIMEOUT:
                    raise ServerLiveMigrationTimeoutException('live migration timeout')

                server = nova_client.servers.get(server)

                logger.debug('server %s is %s', server.id, server.status)
                if is_active(server):
                    return True
                if is_error(server):
                    raise ServerErrorException("server is in error status")
                time.sleep(30)

    def get_status(self, nova_client):

        return nova_client.servers.get(self).status

    @classmethod
    def create(cls, nova_client, name, tag):
        logger = get_logger()
        # fixme vm name duplication?
        # instead it uses database style (mysql...)
        servers = nova_client.servers.list(detailed=False, search_opts={"name": name, "all_tenants": True})

        if len(servers) == 0:
            # this trick utilizes the fact only id attribute is required for this get method
            a = Server(name, None, None, None)
            servers = [nova_client.servers.get(a)]

        if len(servers) == 0:
            # this method might be redundant, nova may support regex natively?
            logger.info('searching through all existing vms, this could be heavy')
            all_servers = get_all_servers(nova_client, name)
            for one in all_servers:
                if re.match(name, one.name):
                    servers.append(one)

        ret = []
        for server in servers:
            detailed_server = nova_client.servers.get(server)
            host = getattr(detailed_server, 'OS-EXT-SRV-ATTR:host')
            vcpus = detailed_server.flavor['vcpus']
            ram = detailed_server.flavor['ram']
            ret.append(Server(server.id, server.name, host, tag, vcpus, ram))

        return ret

    def should_move(self):
        dest = getattr(self, DEST, None)
        if not dest:
            return False
        else:
            return dest != self.host


class ServerErrorException(Exception):
    def __init__(self, *args, **kwargs):
        super(ServerErrorException, self).__init__(*args, **kwargs)
        self.name = 'server error'


class ServerLiveMigrationTimeoutException(Exception):
    def __init__(self, *args, **kwargs):
        super(ServerLiveMigrationTimeoutException, self).__init__(*args, **kwargs)
        self.name = 'live migration timeout'


class ServerErrorStateException(Exception):
    def __init__(self, *args, **kwargs):
        super(ServerErrorStateException, self).__init__(*args, **kwargs)
        self.name = "server in mismatch state"


class ColdMigrationFailedException(Exception):
    def __init__(self, *args, **kwargs):
        super(ColdMigrationFailedException, self).__init__(*args, **kwargs)
        self.name = 'cold migration failed exception'


def is_error(server):
    status = getattr(server, "status")
    if not status:
        return True
    else:
        return status.lower() == 'error'


def is_active(server):
    status = getattr(server, 'status')
    if status:
        return status.lower() == "active"
    else:
        return False


class Host(object):
    def __init__(self, host_id, name, vcpus, ram, **kwargs):
        self.id = host_id
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
        return "%s_%s_%s" % (self.name, self.vcpus, self.ram)

    def __repr__(self):
        return self.__str__()

    def __lt__(self, other):

        # __lt__ return true if self < other
        # be careful: bool(-1) will give True
        if self.vcpus == other.vcpus:
            return self.ram < other.ram
        else:
            return self.vcpus < other.vcpus

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

    hosts = {i.service['host']: Host(i.id, i.service['host'], i.vcpus - i.vcpus_used, i.free_ram_mb)
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

        if correct_aggregate not in aggregates.keys():
            logger.warning("server %s does not have a correct aggregate configured", vm)
            continue

        # move vm if it's on a wrong host
        if current_host not in [i.name for i in aggregates[correct_aggregate].hosts]:
            # compute dest and assign to vm
            hosts = aggregates[correct_aggregate].hosts
            indices = sorted(range(len(hosts)), key=lambda j: hosts[j])
            index = indices[-1]
            logger.info("%s will be moved from %s to %s", vm.id, current_host, hosts[index])
            setattr(vm, DEST, hosts[index].name)

            logger.debug("updating host %s", hosts[index])
            update_host(hosts[index], vm)
            logger.debug("host %s updated", hosts[index])
            # TODO should update current host as well?

    return vms


def read_config(nova_client, config_path):
    # fixme remove duplicate record and log
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
            if col >= MAX_COLUMNS:
                break

            # value should not have letters like 'G'
            val = sheet.cell(row, col).value
            args[COLUME_NAME[col]] = val

        logger.info("args: %s", str(args))
        try:
            servers.extend(Server.create(**args))
        except Exception:
            logger.exception("get server error..")

    # it is hard to know where to find it in excel
    names = {}
    for i in range(len(servers)):
        if not names.get(servers[i].id):
            names[servers[i].id] = [i]
        else:
            names[servers[i].id].append(i)

    dumplicated_index = []
    dumplicated_names = []
    for name in names.keys():
        if len(names[name]) > 1:
            dumplicated_index.extend(names[name])
            dumplicated_names.append(name)
    dumplicated_index = sorted(dumplicated_index, reverse=True)

    # make sure traverse index from greater value to lesser
    for i in dumplicated_index:
        servers.pop(i)

    return servers, dumplicated_names


def tag_and_move_vm(nova_client, vms, preview=False):
    """
    add tag to virtual machines
    :param nova_client:
    :param vms:
    :param preview
    :return:
    """

    ret = {
        "success": [],
        "error": [],
        "ignored": [],
        "preview": []
    }

    waiting_list = Queue()
    server_queue = Queue()
    for vm in vms:
        server_queue.put(vm)

    logger = get_logger()
    while not server_queue.empty():
        logger.debug('retrive server from queue')
        vm = server_queue.get()
        try:
            # tag vm ignoring preview value
            logger.info('start dealing with %s', vm.name)
            vm.tag_vm(nova_client)

            if vm.should_move():
                logger.info('move mv: %s from %s to %s', vm, vm.host, getattr(vm, DEST))

                if not preview:
                    try:
                        # stopped vm couold be resized?
                        vm.migrate(nova_client)
                        vm.start_time = time.time()
                        waiting_list.put(vm)
                    except ServerErrorStateException:
                        logger.exception("vm %s is in wrong state", vm.id)
                        ret['error'].append(vm)
                    except ServerLiveMigrationTimeoutException:
                        logger.exception("waiting for %s finish time out", vm.id)
                        ret['error'].append(vm)
                    except ServerErrorException:
                        logger.exception("server %s is error state", vm.id)
                        ret['error'].append(vm)
                    except Exception:
                        logger.exception("server %s migration failed", vm.id)
                        ret['error'].append(vm)
                else:
                    ret['preview'].append(vm)
                    logger.debug("in preview mode, instance will not be actually moved")
            else:
                ret['ignored'].append(vm)

        except Exception:
            logger.exception("add tag to vm: %s failed", str(vm))
            ret['error'].append(vm)

        while waiting_list.qsize() == WAITING_QUEUE_MAX_SIZE:
            # block here
            vm = waiting_list.get()
            status = check_migrating_vm(nova_client, vm)
            if not status:
                # requeue if not finished
                waiting_list.put(vm)
                time.sleep(10)
            else:
                ret.update(status)

    # searching through waiting list
    logger.info('waiting for live migrating finishes')
    while not waiting_list.empty():
        vm = waiting_list.get()
        status = check_migrating_vm(vm, nova_client)
        if not status:
            # request if not finished
            waiting_list.put(vm)
        else:
            ret.update(status)

    return ret


def check_migrating_vm(nova_client, vm):
    """
    check both cold/live migration
    this makes things tricker since they share different
    :param nova_client:
    :param vm:
    :return:
    """
    ret = {}
    logger = get_logger()
    tic = getattr(vm, "start_time", time.time())
    try:
        status = vm.get_status(nova_client)
        toc = time.time()

        # https://docs.openstack.org/nova/pike/reference/vm-states.html
        if status.lower() in COMPLETED_STATES:
            ret['success'].append(vm)
        elif status.lower() in ERROR_STATE:
            ret['error'].append(vm)
        elif toc - tic > DEFAULT_TIMEOUT:
            ret['error'].append(vm)
        else:
            return None
    except Exception:
        logger.exception("server %s migration failed", vm.id)
        ret['error'].append(vm)

    return ret


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

    endpoint_type = get(credentials, 'endpoin_type', os.environ['OS_ENDPOINT_TYPE'], 'public')
    region_name = get(credentials, 'region_name', os.environ['OS_REGION_NAME'], 'RegionOne')

    nova_client = client.Client('2.53', session=sess, endpoint_type=endpoint_type, region_name=region_name)
    logger.info("initialzing nova client completed successfully")

    # return a glance client
    return nova_client


def get(obj, name, *args):
    """
    extend get(obj, name, default=None) method
    :param obj:
    :param name:
    :param args:
    :return:
    """
    if getattr(obj, name, None):
        return get(obj, name)

    try:
        if isinstance(obj, dict) and obj[name]:
            return obj[name]
    except Exception:
        pass

    for i in args:
        if i:
            return i


def get_all_servers(nova_client, name=None, detailed=False, use_all=True):
    all_servers = []

    opts = {
        "all_tenants": use_all,
    }

    if name:
        opts.update({"name": name})

    last = None
    while True:
        servers = nova_client.servers.list(detailed=detailed, search_opts=opts,
                                           marker=last.id if last else None)
        if len(servers) == 0:
            break
        all_servers.extend(servers)
        last = all_servers[-1]
    return all_servers


def write_vm_to_sheet(vms, sheet):
    attrs = ['name', 'id', 'service', 'host', DEST]

    for i in range(len(attrs)):
        sheet.write(0, i, attrs[i])

    for i in range(len(vms)):
        for j in range(len(attrs)):
            sheet.write(i + 1, j, getattr(vms[i], attrs[j], ''))


def write_to_excel(result, file_name):
    workbook = xlwt.Workbook()
    for key in result.keys():
        sheet = workbook.add_sheet(key)
        write_vm_to_sheet(result[key], sheet)

    workbook.save(file_name)


def get_parser():
    import argparse

    parser = argparse.ArgumentParser(description='generate required flavors')
    parser.add_argument('-f', '--config', dest='config_path', required=True,
                        help='path to the configuration file')
    parser.add_argument('-d', '--debug', dest='debug', action='store_const', const=True,
                        default=False, help='enable debugging')
    parser.add_argument('--no-preview', dest='preview', action='store_const', const=False,
                        default=True, help='preview changes')
    parser.add_argument('-o', '--output', dest='output',
                        default='output.xls', help='display result in excel (xls)')

    return parser.parse_args()


def main():
    parser = get_parser()
    setup_logging(parser.debug)

    nova_client = init_nova_client({})
    logger = get_logger()

    servers, dup = read_config(nova_client, parser.config_path)
    logger.info('%s', servers)
    if len(dup) > 0:
        logger.warning("These names %s are duplicated.", dup)

    logger.info('assemble aggreates objects')
    # aggreates construct relationship between HA -> hosts
    # every HA could have multiple overlapping hosts associated
    aggregates = assemble_aggregates(nova_client)

    logger.info("schedule servers to proper hosts")
    # assign a host to each servers retrieved from excel
    servers = schedule_vms(aggregates, servers)

    logger.info('migrate servers')
    ret = tag_and_move_vm(nova_client, servers, parser.preview)

    logger.info('result is %s', ret)
    write_to_excel(ret, parser.output)


if __name__ == "__main__":
    exit(main())
