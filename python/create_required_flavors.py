#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import logging
from novaclient import client
from keystoneauth1 import session, loading
from xlrd import open_workbook

DEFAULT_SPEC = "GENERAL"
LOGGER = None
COLUME_NAME = ["name", "cpu", "memory", "disk", "spec"]


def get_logger():
    global LOGGER
    if not LOGGER:
        LOGGER = logging.getLogger(__name__)
    return LOGGER


def setup_logging():
    logging.basicConfig(level=logging.INFO)


class Flavor(object):
    """
    flavor object
    """

    def __init__(self, name, cpu, memory, disk, spec):
        """
        initialize object
        :param name: service name
        :param cpu:  cpu number
        :param memory: memory size (in GB)
        :param disk:  hdd size (in GB)
        :param spec: specs no idea its difference between cpu things
        """

        self.name = name
        self.cpu = cpu
        self.memory = memory
        self.disk = disk

        # fixme spec might be a list of string
        if not spec:
            self.spec = [DEFAULT_SPEC]
        elif type(spec) == 'str':
            # string::split will return a list
            # make sure that utf-8 characters will not report error
            self.spec = spec.replace('，', ',').split(',')
        else:
            self.spec = spec

    def __repr__(self):
        """
        customize string representation
        :return:
        """

        template = "%s_%sC%sG%sG_%s"
        return template % (self.name, self.cpu, self.memory, self.disk, "_".join(self.spec))


def read_template_from_excel(config_path):
    """
    read flavor configurations from excel
    :param config_path: path to excel configuration file
    :return: a list of flavors
    """

    logger = get_logger()
    flavors = []

    logger.info("read configuration from %s", config_path)
    wb = open_workbook(config_path)

    # by default, there is only a single sheet
    sheet = wb.get_sheet(0)

    # ignore the first row
    for row in range(1, sheet.nrows):
        args = {}
        for col in range(sheet.ncols):
            # fixme value might have letter like 'G'
            val = sheet.cell(row, col).value
            args[COLUME_NAME[col]] = val
            flavors.append(Flavor(**args))

    logger.info("retrieve %d records from %s", len(flavors), config_path)
    # return a list of Flavors
    return flavors


def create_flavors(nova_client, flavors):
    """
    create all required flavors
    :param nova_client
    :param flavors
    :return:
    """

    logger = get_logger()

    for _flavor in flavors:
        logger.info("create flavor %s", str(_flavor))
        name = str(_flavor)
        cpu = _flavor.cpu
        memory = _flavor.memory
        disk = _flavor.disk

        flavor = nova_client.flavors.create(name, cpu, memory, disk)

        # fixme spec might change later
        flavor.set_keys({
            "SPEC": _flavor.spec[0],
            "SERVICE": _flavor.name
        })


def init_nova_client(credentials):
    # get logger
    logger = get_logger()

    # relation between variable name & corresponding environment variable
    required_fields = {'auth_url': 'OS_AUTH_URL',
                       'username': "OS_USERNAME",
                       'password': 'OS_PASSWORD',
                       'domain_name': "OS_USER_DOMAIN_NAME",
                       'project_name': "OS_PROJECT_NAME",
                       'project_domain_name': "OS_PROJECT_DOMAIN_NAME"
                       }

    # check & pop values from environment variable
    for key in required_fields.keys():
        if not credentials.get(key):
            value = os.environ[required_fields[key]]
            if not value:
                raise Exception("%s(%s) is missing" % (key, required_fields[key]))
            else:
                credentials.update({key: value})

    logger.info("begin initializing nova client")
    loader = loading.get_plugin_loader('v3password')
    auth = loader.load_from_options(**credentials)

    sess = session.Session(auth=auth)
    nova_client = client.Client('latest', session=sess, verify=False, endpoint_type="public", region_name="RegionOne")
    logger.info("initialzing nova client completed successfully")

    # return a glance client
    return nova_client


def main():
    """
    program entrance
    :return:
    """

    args = sys.argv

    return 0


if __name__ == "__main__":
    exit(main())
