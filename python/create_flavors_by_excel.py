#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import xlrd
import os
from keystoneauth1 import loading, session
from novaclient import client as novac

AUTH_URL = ''
USERNAME = 'admin'
PASSWORD = ''
PROJECT_NAME = 'admin'
DOMAIN_NAME = 'Default'
DOMAIN_ID = 'default'
VERSION = '2.30'

INPUT_FILE = "flavor_info.xlsx"
INPUT_TITTLES = ['SERVICE', 'CPU', 'MEMORY', 'DISK', 'SPEC']


def get_nova_client():
    loader = loading.get_plugin_loader('password')
    auth = loader.load_from_options(auth_url=AUTH_URL,
                                    username=USERNAME,
                                    password=PASSWORD,
                                    project_name=PROJECT_NAME,
                                    user_domain_name=DOMAIN_NAME,
                                    project_domain_name=DOMAIN_NAME)
    sess = session.Session(auth=auth, verify=False)
    return novac.Client(VERSION, session=sess, endpoint_type='internal')


def get_parse():
    import argparse
    parser = argparse.ArgumentParser(description="parses information:")
    parser.add_argument('-i', '--input', dest='conf_path', help='Input server information excel file path.',
                        default=INPUT_FILE)
    return parser.parse_args()


def read_conf(file=INPUT_FILE):
    if os.path.exists(file):
        readbook = xlrd.open_workbook(file)
        return readbook
    else:
        print "Error: Config File:" + file + " is not existed."
        return None


def generate_name(service, cpu, memory, disk, spec):
    flavor_name = service.lower() + "_" + str(cpu) + "C" + str(memory) + "G" + str(disk) + "G" + "_" + spec.lower()
    return flavor_name


def generate_metadata(service, spec):
    metadata = {"SERVICE": service, "SPEC": spec.upper()}
    return metadata


def main():
    params = get_parse()

    workbook = read_conf(file=params.conf_path)

    if not workbook:
        print "Error: Please input correct config file path."
        raise Exception("path: %s does not exist!", params.conf_path)

    novaclient = get_nova_client()
    rsheet = workbook.sheet_by_name("create_flavors")
    for row in range(1, rsheet.nrows):
        # service is strict,do not use lower
        try:
            service = rsheet.cell_value(row, INPUT_TITTLES.index('SERVICE'))
            cpu = int(rsheet.cell_value(row, INPUT_TITTLES.index('CPU')))
            memory = int(rsheet.cell_value(row, INPUT_TITTLES.index('MEMORY')))
            disk = int(rsheet.cell_value(row, INPUT_TITTLES.index('DISK')))
            spec = rsheet.cell_value(row, INPUT_TITTLES.index('SPEC'))
        except Exception as e:
            print "Error: Read config file failed.   Failed RowNum=" + (row)
            print e
            print "________________________________________________"
            continue

        name = generate_name(service, cpu, memory, disk, spec)
        metadata = generate_metadata(service, spec)
        print "Info: Create flavor name=" + name + " cpu:" + str(cpu) + " memory:" + str(memory) + "G disk:" + str(
            disk) + "G spec:" + spec
        print "Info: Metadata"
        print metadata
        try:
            flavor = novaclient.flavors.create(name=name, ram=memory * 1024, vcpus=cpu, disk=disk)
            print "Info: Create flavor success.Flavor ID="+flavor.id
            flavor = flavor.set_keys(metadata)
            print "Info: Set Metadata success."
        except Exception as e:
            print "Error: Create flavor & set Metadata failed."
            print e
        print "________________________________________________"


if __name__ == '__main__':
    sys.exit(main())
