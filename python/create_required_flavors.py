#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import re
import sys

from keystoneauth1 import session, loading
from novaclient import client
from xlrd import open_workbook

DEFAULT_SPEC = "general"
LOGGER = None
COLUME_NAME = ["name", "cpu", "memory", "disk", "bandwidth", "spec"]
MAX_COLUMNS = len(COLUME_NAME)
_FLAVORS = None


def get_logger():
    global LOGGER
    if not LOGGER:
        LOGGER = logging.getLogger(__name__)
    return LOGGER


def setup_logging(debug=False):
    level = logging.DEBUG if debug else logging.INFO
    logging_format = "[%(asctime)s] - %(levelname)s - %(name)s.%(lineno)s - %(message)s"
    logging.basicConfig(level=level, format=logging_format)


class Flavor(object):
    """
    flavor object
    """

    def __init__(self, name, cpu, memory, disk, bandwidth=0, spec=None):
        """
        initialize object
        :param name: service name
        :param cpu:  cpu number
        :param memory: memory size (in GB)
        :param disk:  hdd size (in GB)
        :param spec: specs no idea its difference between cpu things
        """

        self.name = name
        self.service = name
        self.cpu = str(int(cpu))
        self.memory = str(int(memory))
        self.disk = str(int(disk))

        self.bandwidth = int(bandwidth) if bandwidth > 0 else 0

        # fixme spec might be a list of string
        if not spec:
            self.spec = [DEFAULT_SPEC]
        elif isinstance(spec, str):
            # string::split will return a list
            # make sure that utf-8 characters will not report error
            self.spec = spec.replace(u'，', ',').split(',')
        else:
            self.spec = spec

        logger = get_logger()
        logger.debug("<%s-%s-%s-%s-%s-%s>", name, cpu, memory, disk, bandwidth, self.spec)

    @property
    def service_name(self):
        return self.name

    @property
    def spec_name(self):
        return self.spec.upper()

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        """
        customize string representation
        :return:
        """

        template = "%s_%sC%sG%sG_%s"
        return template % (self.name.lower(), self.cpu, self.memory, self.disk, "_".join(self.spec))

    @classmethod
    def create(cls, name, cpu, memory, disk, bandwidth=0, spec=None):
        """
        create flavors
        :param name:
        :param cpu:
        :param memory:
        :param disk:
        :param bandwidth
        :param spec:
        :return: return a list of flavors
        """

        if not spec:
            spec = DEFAULT_SPEC

        cpu_tuple = split_string(cpu)
        ram_tuple = split_string(memory)
        disk_tuple = split_string(disk)

        if not bandwidth:
            bandwidth = 0

        flavors = [cls(name, c, r, d, bandwidth, spec) for c in range(*cpu_tuple) for r in range(*ram_tuple) for d in
                   range(*disk_tuple)]
        return flavors


class ClassicFlavor(Flavor):

    def __init__(self, name, cpu, memory, disk, bandwidth=0, spec=None):
        super(ClassicFlavor, self).__init__(name, cpu, memory, disk, bandwidth, spec)
        self.name = name
        self.service = "ECS"

    def __repr__(self):
        return self.name


def split_string(val):
    """
    a helper function
    this function does not handle a value with unit associated
    :param val: either int or values separated by comma
    :return: a tuple of min, max, step
    """

    # do not use raw string
    pattern = ur"，|,"
    if (isinstance(val, str) or isinstance(val, unicode)) and re.search(pattern, val):
        arr = val.replace(u'，', ',').split(',')[0:3]
        a = int(arr[0])
        b = int(arr[1])
        c = int(arr[2])
        return a, c + b * zero_to_one((c - a) % b), b
    else:
        return int(val), int(val) + 1, 1


def zero_to_one(x):
    return 1 if x == 0 else 0


def read_template_from_excel(config_path, flavor_cls, index=0):
    """
    read flavor configurations from excel
    :param config_path: path to excel configuration file
    :param flavor_cls: class object of Flavor
                        possible Flavor, ClassicFlavor
    :return: a list of flavors
    """

    if not os.path.exists(config_path):
        raise Exception("path: %s does not exist!", config_path)

    logger = get_logger()
    flavors = []

    logger.info("read configuration from %s", config_path)
    wb = open_workbook(config_path)

    sheet = wb.sheets()[index]

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
        flavors.extend(flavor_cls.create(**args))

    logger.info("retrieve %s records from %s", str(flavors), config_path)
    # return a list of Flavors
    return flavors


def retrieve_all_flavors(nova_client):
    global _FLAVORS
    if _FLAVORS:
        return _FLAVORS
    else:
        total_flavors = []

        # return has an upper limit of 1000
        last_one_marker = None
        while True:
            flavors = nova_client.flavors.list(detailed=False, marker=last_one_marker.id if last_one_marker else None)
            if len(flavors) == 0:
                break
            total_flavors.extend(flavors)
            last_one_marker = flavors[-1]
        _FLAVORS = total_flavors
        return _FLAVORS


def get_flavor(nova_client, flavor_name):
    """
    get flavor by its name
    :param nova_client:
    :param flavor_name:
    :return:
    """

    # total_flavors = []
    #
    # # return has an upper limit of 1000
    # last_one_marker = None
    # while True:
    #     flavors = nova_client.flavors.list(detailed=False, marker=last_one_marker.id if last_one_marker else None)
    #     if len(flavors) == 0:
    #         break
    #     total_flavors.extend(flavors)
    #     last_one_marker = flavors[-1]
    total_flavors = retrieve_all_flavors(nova_client)

    for flavor in total_flavors:
        if flavor.name == flavor_name:
            return flavor

    return None


def create_flavors(nova_client, flavors):
    """
    create all required flavors
    :param nova_client
    :param flavors
    :return:
    """

    if not nova_client:
        raise Exception("nova client has not been properly setup!")

    logger = get_logger()

    for _flavor in flavors:
        try:
            create_flavor(nova_client, _flavor)
        except Exception:
            logger.exception("create flavor: %s failed", str(_flavor))


def create_flavor(nova_client, flavor):
    """
    create a flavor
    :param nova_client:
    :param flavor:
    :return:
    """

    logger = get_logger()
    logger.info("create flavor %s", str(flavor))
    name = str(flavor)
    cpu = flavor.cpu

    # by convention, memory is in GB
    memory = int(flavor.memory) * 1024
    disk = flavor.disk

    _flavor = get_flavor(nova_client, name)
    # remove duplicate flavor
    if _flavor:
        logger.warning("flavor: %s already exists", name)
        _flavor.delete()

    _flavor = nova_client.flavors.create(name, memory, cpu, disk)

    # set method should be idempotent

    flavor_keys = {
        "SPEC": flavor.spec[0].upper(),
        "SERVICE": flavor.service
    }

    if flavor.bandwidth > 0:
        flavor_keys.update({
            "quota:vif_inbound_average": str(int(flavor.bandwidth * 1024 * 1024)),
            "quota:vif_outbound_average": str(int(flavor.bandwidth * 1024 * 1024))
        })

    logger.debug('flavor(%s) keys are %s', str(flavor), flavor_keys)
    _flavor.set_keys(flavor_keys)


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
    parser.add_argument('-t', '--type', dest='type', default="Flavor", help='ClassicFlavor/Flavor')
    parser.add_argument('-i', '--index', dest='index', type=int, default=0, help='index of excel sheet')
    parser.add_argument('-d', '--debug', dest='debug', action='store_const', const=True,
                        default=False, help='enable debugging')

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
    flavor_cls_name = parser.type
    index = parser.index
    flavors = read_template_from_excel(parser.config_path, getattr(sys.modules[__name__], flavor_cls_name), index=index)

    # init nova client
    nova_client = init_nova_client({})

    # create requested flavors
    logging.info("start creating flavors")
    create_flavors(nova_client, flavors)
    logging.info("finishes creating flavors")
    return 0


if __name__ == "__main__":
    exit(main())
