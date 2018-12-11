#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging
import os
import re

import xlwt
from keystoneauth1 import session, loading
from neutronclient.v2_0 import client
from xlrd import open_workbook

DEFAULT_SPEC = "general"
LOGGER = None
COLUME_NAME = ["service", "network_name", "subnet_name", "cidr", "ip_pool", "vlanid", "disable_dhcp", 'disable_gw',
               'gw', 'dns', 'host_routes']
MAX_COLUMNS = len(COLUME_NAME)
DEFAULT_NIC = "physnet1"


def get_logger():
    global LOGGER
    if not LOGGER:
        LOGGER = logging.getLogger(__name__)
    return LOGGER


def setup_logging(debug=False):
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level)


class Network(object):
    """
    network object
    """

    def __init__(self, service, network_name, subnet_name, cidr, ip_pool, vlanid, disable_dhcp=u'否', disable_gw=u'否',
                 gw=None, dns=None, host_routes=None):
        """

        :param service:
        :param network_name:
        :param subnet_name:
        :param cidr:
        :param disable_dhcp:
        :param ip_pool:
        :param vlanid:
        :param disable_gw:
        :param gw:
        :param dns:
        """

        # fixme input error?
        self.network_id = None
        self.service = service
        self.network_name = network_name
        self.subnet_name = subnet_name
        self.subnet_id = None
        self.cidr = cidr

        # disable dhcp
        if re.search(u'是', disable_dhcp):
            self.disable_dhcp = True
        else:
            self.disable_dhcp = False

        self.ip_pool = ip_pool
        self.vlanid = str(int(vlanid)) if isinstance(vlanid, float) else vlanid

        # disable gateway
        if re.search(u'是', disable_gw):
            self.disable_gw = True
        else:
            self.disable_gw = False

        self.gw = gw
        self.dns = dns
        self.host_routes = host_routes

    def create_network(self, neutron_client):

        if not neutron_client:
            raise Exception("Please initialize neutron client before continuing")

        logger = get_logger()

        # fixme network_name may be similar, change it to exact match
        networks = neutron_client.list_networks(name=self.network_name).get('networks')

        # create network if not existing
        if len(networks) == 0:
            # create this network
            network = neutron_client.create_network(self.network).get('network')
        elif len(networks) == 1:
            # already exist
            network = networks[0]
        else:
            raise Exception("There are multiple networks with same name, please check config")

        self.network_id = network.get('id')
        # create subnet if not existings
        logger.info("network id: %s", self.network_id)
        subnets = neutron_client.list_subnets(**{
            "network_id": network.get('id')
        }).get('subnets')

        logging.info("subnets obtained %s", str(subnets))
        if len(subnets) == 0:
            subnet = neutron_client.create_subnet(self.get_subnet(network.get('id'))).get('subnet')
            self.subnet_id = subnet.get('id')
        else:
            logger.warning("subnet: %s is duplicate, maybe it has been created already?", self.subnet_name)
            self.subnet_id = subnets[0].get('id')

    @property
    def network(self):
        network = {
            "network": {
                "name": self.network_name,
                # fixme configurable or not?
                "provider:network_type": "vlan",
                # fixme configrable or not?
                "provider:physical_network": DEFAULT_NIC,
                "provider:segmentation_id": self.vlanid,
                "shared": True,
                "router:external": False
            }}

        return network

    def get_subnet(self, network_id):
        subnet = {
            "subnet": {
                "network_id": network_id,
                "name": self.subnet_name,
                "ip_version": 4,
                "cidr": self.cidr
            }
        }

        if self.dns and len(self.dns) > 0:
            subnet['subnet'].update({"dns_nameservers": self.dns.replace(u'，', ',').split(',')})

        if self.disable_dhcp:
            subnet['subnet'].update({"enable_dhcp": False})

        if not self.disable_gw and self.gw:
            subnet['subnet'].update({"gateway_ip": self.gw})

        if self.disable_gw:
            subnet['subnet'].update({"gateway_ip": None})

        if self.ip_pool:
            pool = self.ip_pool.replace(u'，', ',').replace(u'；', ";").rstrip(';')
            subnet['subnet'].update(
                {"allocation_pools": [dict_zip(i.split(',')[0:2], ['start', 'end']) for i in pool.split(';')]})

        # https://developer.openstack.org/api-ref/network/v2/index.html?expanded=create-network-detail,create-subnet-detail#create-subnet
        if self.gw and self.host_routes:
            host_routes = [{"destination": i, "nexthop": self.gw} for i in
                           self.host_routes.replace(u'，', ',').split(',')]
            subnet['subnet'].update({"host_routes": host_routes})

        return subnet


def dict_zip(a, b):
    """
    take two list [a,b,c] and [d,e,f]
    and return a dict {a:d, b:e, c:f}
    :param a:
    :param b:
    :return:
    """
    min_len = len(b) if len(b) < len(a) else len(a)
    ret = {}
    for i in range(min_len):
        ret[b[i]] = a[i]
    return ret


def read_template_from_excel(config_path):
    """
    read flavor configurations from excel
    :param config_path: path to excel configuration file
    :return: a list of flavors
    """

    if not os.path.exists(config_path):
        raise Exception("path: %s does not exist!", config_path)

    logger = get_logger()
    networks = []

    logger.info("read configuration from %s", config_path)
    wb = open_workbook(config_path)

    # by default, there is only a single sheet
    sheet = wb.sheets()[0]

    # ignore the first row
    for row in range(1, sheet.nrows):
        args = {}
        for col in range(sheet.ncols):

            # there should not be more than defined
            # number of columns
            if col > MAX_COLUMNS:
                break

            val = sheet.cell(row, col).value
            args[COLUME_NAME[col]] = val

        logger.info("args: %s", str(args))
        networks.append(Network(**args))

    logger.info("retrieve %s records from %s", str(networks), config_path)
    # return a list of Flavors
    return networks


def create_networks(neutron_client, networks):
    """
    create all required flavors
    :param neutron_client
    :param networks
    :return:
    """

    if not neutron_client:
        raise Exception("neutron client has not been properly setup!")

    logger = get_logger()

    for network in networks:
        logger.info("create network %s", str(network))
        try:
            network.create_network(neutron_client)
            logger.info('successfully create network:subnet %s:%s', network.network_name, network.subnet_name)
        except Exception as e:
            logger.error("create network:subnet %s:%s failed, %s", network.network_name, network.subnet_name, e)


def init_neutron_client(credentials):
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

    nova_client = client.Client(session=sess, endpoint_type=endpoint_type, region_name=region_name)
    logger.info("initialzing neutron client completed successfully")

    # return a glance client
    return nova_client


def write_output_to_excel(networks, filename):
    """
    write networks output to filename
    :param networks:
    :param filename:
    :return:
    """

    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet("networks")

    attrs = ["service", 'network_id', "network_name", "subnet_id", "subnet_name"]

    for i in range(len(attrs)):
        sheet.write(0, i, attrs[i])

    for j in range(len(networks)):
        for i in range(len(attrs)):
            sheet.write(1 + j, i, getattr(networks[j], attrs[i], ''))

    workbook.save(filename)


def get_parser():
    import argparse

    parser = argparse.ArgumentParser(description='generate required flavors')
    parser.add_argument('-f', '--config', dest='config_path', required=True,
                        help='path to the configuration file')
    parser.add_argument('-d', '--debug', dest='debug', action='store_const', const=True,
                        default=False, help='enable debugging')
    parser.add_argument('-o', '--ouput', dest='output_file', default="networks.xls", help='write output to file')

    return parser.parse_args()


def main():
    """
    program entrance
    :return:
    """

    parser = get_parser()

    # setup loggings
    setup_logging(debug=parser.debug)

    # assemble flavor objects
    logger = get_logger()
    logger.info('configuration found at %s', parser.config_path)
    networks = read_template_from_excel(parser.config_path)

    # init nova client
    # fixme read credentials from command line & config files?
    neutron_client = init_neutron_client({})

    # create requested flavors
    create_networks(neutron_client, networks)

    # output to excel
    if not parser.output_file:
        return 0
    write_output_to_excel(networks, parser.output_file)

    return 0


if __name__ == "__main__":
    # fixme init project?
    exit(main())
