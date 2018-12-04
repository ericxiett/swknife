#coding=utf-8
import os
import sys

import xlrd
from keystoneauth1 import loading, session
from novaclient import client as novac


AUTH_URL = 'http://192.168.2.11:35357/v3'
USERNAME = 'admin'
PASSWORD = '89rqdHLMN5rm0x1P'
PROJECT_NAME = 'admin'
DOMAIN_NAME = 'Default'
DOMAIN_ID = 'default'
VERSION = '2.1'


def get_nova_client():
    loader = loading.get_plugin_loader('password')
    auth = loader.load_from_options(auth_url=AUTH_URL,
                                    username=USERNAME,
                                    password=PASSWORD,
                                    project_name=PROJECT_NAME,
                                    user_domain_name=DOMAIN_NAME,
                                    project_domain_name=DOMAIN_NAME)
    sess = session.Session(auth=auth)
    return novac.Client(VERSION, session=sess, endpoint_type='internal')


def parse_xls(xls_file):
    if not os.path.exists(xls_file):
        print('%s not found' % xls_file)
        return None

    book = xlrd.open_workbook(xls_file)
    sheet = book.sheet_by_name('vm_list')
    vms = []
    for row in range(2, sheet.nrows):
        uuid = sheet.cell_value(row, 3)
        old_name = sheet.cell_value(row, 1)
        new_name = sheet.cell_value(row, 4)
        vms.append({
            'uuid': uuid,
            'old_name': old_name,
            'new_name': new_name
        })
    return vms


def rename_vms(vms):
    nc = get_nova_client()
    for vm in vms:
        vm_info = nc.servers.get(vm.get('uuid'))
        if vm_info.name != vm.get('old_name'):
            print('%s is not %s from xls file!' % (vm_info.name, vm.get('old_name')))
            continue
        updated_info = nc.servers.update(vm.get('new_name'))
        print('Result name: %s' % updated_info.name)


def main():
    if len(sys.argv) < 2:
        print('Please input xls file!')
        exit(1)

    xls_file = sys.argv[1]
    vms = parse_xls(xls_file)
    if not vms:
        exit(2)

    rename_vms(vms)


if __name__ == '__main__':
    sys.exit(main())