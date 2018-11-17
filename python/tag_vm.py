#!/usr/bin/python env
# -*- coding: utf-8 -*-

import sys
import re
import logging
import os
from xlrd import open_workbook
from novaclient import client
from keystoneauth1 import loading, session

LOGGER = None
MAX_COLUMNS = 2
COLUME_NAME = ["name", "tag"]


def setup_logging(debug=False):
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level)


def get_logger():
    global LOGGER
    if not LOGGER:
        LOGGER = logging.getLogger(__name__)
    return LOGGER


class Server(object):

    def __init__(self, name, tag):

        # this id will not be used if
        # search name returns a list with more than 1 element
        self.id = name
        self.name = name
        self.tag = tag

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "%s_%s_%s" % (self.id, self.name, self.tag)

    def tag_vm(self, nova_client):
        """
        tag vm
        :param nova_client:
        :return:
        """

        logger = get_logger()
        # fixme openstack does not support normal regex
        # instead it uses database style (mysql...)
        servers = nova_client.servers.list(detailed=False, search_opts={"name": self.name, "all_tenants": True})

        if len(servers) == 0:
            # this trick utilizes the fact only id attribute is required for this get method
            servers = [nova_client.servers.get(self)]

        if len(servers) == 0:
            # this method might be redundant, nova may support regex natively?
            # fixme Number of servers > default limit?
            logger.info('searching through all existing vms, this could be heavy')
            all_servers = nova_client.servers.list(detailed=False, search_opts={"all_tenants": True})
            for one in all_servers:
                if re.match(self.name, one.name):
                    servers.append(one)

        # tag this vm
        for concise_server in servers:
            tag_list = [i for i in nova_client.servers.tag_list(concise_server)]
            if self.tag not in tag_list:
                logger.info('create tag %s for vm %s (%s)', self.tag, self.name, concise_server.id)
                nova_client.servers.add_tag(concise_server, self.tag)
            else:
                logger.info('vm: %s(%s) already has tag: %s', self.name, concise_server.id, self.tag)

    @classmethod
    def create(cls, name, tag):
        return Server(name, tag)


def read_config(config_path):
    if not os.path.exists(config_path):
        raise Exception("path: %s does not exist!", config_path)

    logger = get_logger()
    flavors = []

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

            # fixme value might have letter like 'G'
            val = sheet.cell(row, col).value
            args[COLUME_NAME[col]] = val

        logger.info("args: %s", str(args))
        flavors.append(Server.create(**args))

    return flavors


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


def get_parser():
    import argparse

    parser = argparse.ArgumentParser(description='generate required flavors')
    parser.add_argument('-f', '--config', dest='config_path', required=True,
                        help='path to the configuration file')
    parser.add_argument('-d', '--debug', dest='debug', action='store_const', const=True,
                        default=False, help='enable debugging')

    return parser.parse_args()


def main():
    parser = get_parser()
    setup_logging(parser.debug)

    # fixme init credentials
    nova_client = init_nova_client({})
    tag_vm(nova_client, read_config(parser.config_path))
    return 0


if __name__ == "__main__":
    exit(main())
