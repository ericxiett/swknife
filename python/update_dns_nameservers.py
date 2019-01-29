#!/usr/bin/python env
# -*- coding: utf-8 -*-

import logging
import os
import re

from keystoneauth1 import loading, session
from neutronclient.v2_0 import client

logging.basicConfig(level=logging.INFO)


def get_parser():
    import argparse

    parser = argparse.ArgumentParser(description='generate required flavors')
    parser.add_argument('-f', '--file', dest='sql_file', required=True,
                        help='path to SQL file')
    parser.add_argument('-p', '--plot', dest='plot', action='store_true', default=False)
    parser.add_argument('-n', '--nameservers', dest='nameservers', default=None, action='append',
                        help='list of nameservers')
    return parser.parse_args()


def strip_non_letters(input_str):
    pattern = r"[a-zA-Z0-9\-_.].*[a-zA-Z0-9\-_.]"
    match = re.search(pattern, input_str)
    return match.group(0) if match else input_str[1:-1]


class SQLTranslator(object):
    """
    a simple SQL translator by evaludating regular expressions
    """

    def __init__(self, text):
        super(SQLTranslator, self).__init__()
        self.text = text
        self.logger = logging.getLogger(type(self).__name__)

    def translate(self, delimiter=';'):
        objs = []
        for i in self.text.split(delimiter):
            try:
                obj = {}
                sql = i.strip()

                # continue if empty string
                if sql == '':
                    continue

                # matching parenthesis
                pattern = r"^.*?\((.*)\).*?\((.*)\).*?$"
                match = re.match(pattern, sql)

                # it will complain if pattern does not match
                names, values = match.group(1), match.group(2)

                # zipping arr1, arr2 together does not work
                # apparently there are some unicode issues
                arr1 = values.split(',')
                arr2 = names.split(',')
                for i in range(min(len(arr1), len(arr2))):
                    obj[strip_non_letters(arr2[i])] = strip_non_letters(arr1[i])
                objs.append(obj)
            except Exception:
                logger.exception("error occured while evaluating: %s", i)
        return objs


def init_neutron_client(credentials):
    # get logger
    logger = logging.getLogger()

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

    logger.info("begin initializing neutron client")
    loader = loading.get_plugin_loader('v3password')
    auth = loader.load_from_options(**options)
    sess = session.Session(auth=auth, verify=False)
    endpoint_type = credentials.get('endpoint_type', os.environ['OS_ENDPOINT_TYPE'])
    endpoint_type = endpoint_type if endpoint_type else "public"
    region_name = credentials.get('region_name', os.environ['OS_REGION_NAME'])
    region_name = region_name if region_name else "RegionOne"
    return client.Client(session=sess, endpoint_type=endpoint_type, region_name=region_name)


def get_nameservers(subnet):
    return subnet.get('subnet', {}).get('dns_nameservers', [])


def set_nameserver(client, subnet_id, nameservers):
    client.update_subnet(subnet_id, {
        'subnet': {
            "dns_nameservers": nameservers
        }
    })


def plot(dataset):
    import matplotlib.pyplot as plt
    import numpy as np
    t = np.arange(1, len(dataset.keys()) + 1)
    fig, ax = plt.subplots()
    plt.bar(t, tuple(dataset.values()))
    ax.set_xticks(t)
    ax.set_xticklabels(dataset.keys(), rotation='60')
    plt.show()
    # plt.savefig('test.png')


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    parser = get_parser()
    targets = []
    with open(parser.sql_file, 'rb') as f:
        lines = "".join(f.readlines())
        targets.extend(SQLTranslator(lines).translate())
    logger.debug(targets)

    neutron_client = init_neutron_client({})
    new_namservers = parser.nameservers
    dns_nameserver_dict = {}

    for network in targets:
        subnet_id = network.get('subnet_id', None)
        if not subnet_id:
            continue

        if new_namservers:
            set_nameserver(neutron_client, subnet_id, new_namservers)

        subnet = neutron_client.show_subnet(subnet_id)
        nameservers = get_nameservers(subnet)
        if len(nameservers) == 0:
            nameservers.append(None)
        for n in nameservers:
            if dns_nameserver_dict.get(n, None):
                dns_nameserver_dict[n] = dns_nameserver_dict[n] + 1
            else:
                dns_nameserver_dict[n] = 1
    if parser.plot:
        plot(dns_nameserver_dict)
