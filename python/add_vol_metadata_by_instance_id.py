#coding=utf-8
import os
import sys
import time

import xlrd
from keystoneauth1 import loading, session
from cinderclient import client as clientc
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


def parse_xls_file(xls_file):

    book = xlrd.open_workbook(xls_file)
    sheet = book.sheet_by_name('vms')
    vms = []
    for row in range(1, sheet.nrows):
        vms.append(sheet.cell_value(row, 0))

    return vms


def get_vols_by_id(vms):
    vols = []
    nc = get_nova_client()
    for vid in vms:
        print('Get vm %s ...' % vid)
        try:
            vm_info = nc.servers.get(vid)
            print('vm info: %s' % vm_info)
            for vol in vm_info.__dict__['os-extended-volumes:volumes_attached']:
                vols.append(vol['id'])
        except Exception as e:
            print('Got error %s' % e)
            continue

    return vols


def get_cinder_client():
    loader = loading.get_plugin_loader('password')
    auth = loader.load_from_options(auth_url=AUTH_URL,
                                    username=USERNAME,
                                    password=PASSWORD,
                                    project_name=PROJECT_NAME,
                                    user_domain_name=DOMAIN_NAME,
                                    project_domain_name=DOMAIN_NAME)
    sess = session.Session(auth=auth)
    return clientc.Client('3', session=sess, endpoint_type='internal')


def add_metadata_to_vol(vols):
    cc = get_cinder_client()
    for vid in vols:
        try:
            vol = cc.volumes.get(vid)
            meta = {'productTag': 'CKS'}
            cc.volumes.set_metadata(vol, meta)
            time.sleep(2)
            vol = cc.volumes.get(vid)
            print('%s meta: %s' % (vid, vol.metadata))
        except Exception as e:
            print('Got error %s' % e)
            continue


def main():
    if len(sys.argv) < 2 or not os.path.exists(sys.argv[1]):
        print('Please input valid xls file!')
        exit(1)

    vms = parse_xls_file(sys.argv[1])
    vols = get_vols_by_id(vms)
    add_metadata_to_vol(vols)


if __name__ == '__main__':
    sys.exit(main())
