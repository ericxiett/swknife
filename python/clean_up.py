# -*- coding: UTF-8 -*-
# Clean up resources
import os
import sys

import xlrd
from keystoneauth1 import loading, session
from novaclient import client


def parse_resources():
    xls_file = 'cloud_res.xls'
    if not os.path.exists(xls_file):
        print('Error: cloud_res.xls not exist!')
        raise Exception('Error: cloud_res.xls not exist!')

    book = xlrd.open_workbook(xls_file)
    sheet = book.sheet_by_name('reserved_vms')
    reserved = []
    for row in range(1, sheet.nrows):
        vm_uuid = sheet.cell_value(row, 0)
        print('%s: %s' % (row, vm_uuid))
        reserved.append(vm_uuid)

    return reserved


def get_nova_client():
    loader = loading.get_plugin_loader('password')
    auth = loader.load_from_options(
        auth_url=os.environ.get('OS_AUTH_URL'),
        username=os.environ.get('OS_USERNAME'),
        password=os.environ.get('OS_PASSWORD'),
        project_name=os.environ.get('OS_PROJECT_NAME'),
        user_domain_name=os.environ.get('OS_USER_DOMAIN_NAME'),
        project_domain_name=os.environ.get('OS_PROJECT_DOMAIN_NAME'))
    sess = session.Session(auth=auth)
    return client.Client('2.1', session=sess, endpoint_type='internal')


def clean_up(reserved):
    novac = get_nova_client()
    vms = novac.servers.list(search_opts={'all_tenants': True})
    for vm in vms:
        if vm.id not in reserved and \
                ('ECS' in vm.name or 'test' in vm.name):
            print('VM ID %s %s should be deleted' % (vm.id, vm.name))
            #novac.servers.force_delete(vm.id)


def main():
    reserved = parse_resources()
    clean_up(reserved)



if __name__ == '__main__':
    sys.exit(main())
