#coding=utf-8
import os
import sys
import time

import xlrd
from keystoneauth1 import loading, session
from cinderclient import client as clientc


AUTH_URL = 'http://192.168.2.11:35357/v3'
USERNAME = 'admin'
PASSWORD = '89rqdHLMN5rm0x1P'
PROJECT_NAME = 'admin'
DOMAIN_NAME = 'Default'
DOMAIN_ID = 'default'
VERSION = '2.1'


def get_cinder_client():
    loader = loading.get_plugin_loader('password')
    auth = loader.load_from_options(auth_url=AUTH_URL,
                                    username=USERNAME,
                                    password=PASSWORD,
                                    project_name=PROJECT_NAME,
                                    user_domain_name=DOMAIN_NAME,
                                    project_domain_name=DOMAIN_NAME)
    sess = session.Session(auth=auth)
    return clientc.Client(VERSION, session=sess, endpoint_type='internal')


def main():
    print('welcome to use this scripts to add volume metadata..')
    cinder = get_cinder_client()
    vollist = cinder.volumes.list()
    #find out unset metadata volumes
    try:
        print('find out unset metadata volumes ..')
        for volume in vollist:
            volfilter(volume=volume)
    except Exception as e:
        print(e.message)


def volfilter(volume):
    try:
        vols = []
        cinder = get_cinder_client()
        vid = cinder.volumes.get(volume)
        md = vid.metadata
        if 'productTag' not in md:
            vols = vols.append(volume)
        add_metadata_to_vol(vols=vols)
    except Exception as e:
        print(e.message)


def add_metadata_to_vol(vols):
    cc = get_cinder_client()
    for vid in vols:
        try:
            vol = cc.volumes.get(vid)
            meta = {'productTag': 'ebs'}
            cc.volumes.set_metadata(vol, meta)
            time.sleep(2)
            vol = cc.volumes.get(vid)
            print('%s meta: %s' % (vid, vol.metadata))
        except Exception as e:
            print('Got error %s' % e)
            continue


if __name__ == '__main__':
    sys.exit(main())