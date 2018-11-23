#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import xlrd
# import random
# import string
from keystoneauth1 import loading, session
from cinderclient import client as clientc


AUTH_URL = 'http://controller:5000/v3'
USERNAME = 'admin'
PASSWORD = 'cobbler'
PROJECT_NAME = 'admin'
DOMAIN_NAME = 'Default'
DOMAIN_ID = 'default'
VERSION = '3'


def main():
    print('welcome to use this scripts to create volumetypes..')
    print('Welcome to use this script to create volumetypes...')
    if len(sys.argv) < 2:
        print('Please input valid the path of volumetypesFile.')
        exit(1)
    XLS_FILE = sys.argv[1]
    init_check(XLS_FILE=XLS_FILE)


def init_check(XLS_FILE):
    # read volumetype config file
    if os.path.exists(XLS_FILE):
        book = xlrd.open_workbook(XLS_FILE)
        sheet = book.sheet_by_name('Sheet1')
    else:
        print('Error: volumetype config file' + XLS_FILE + 'is not exit')
        return 0
    # get cinder_client
    cinder = get_cinder_client()
    # # get all old volumetypes
    # vtypeList = cinder.volume_types.list()
    # # delete exited volumetypes
    # try:
    #     print("Warning:Deleting all exited Volume_Types")
    #     for volume_types in vtypeList:
    #         vt_delete(volume_types=volume_types)
    # except Exception as e:
    #     print(e.message)
    # # renaming all volumeTypes that were been using
    # vtypeList2 = cinder.volume_types.list()
    # for volume_types in vtypeList2:
    #     vtname = volume_types.name
    #     middle_name = ''.join(random.sample(string.ascii_letters+string.digits, 6))
    #     rename = vtname+"_"+middle_name
    #     print("Warning:renaming Volume_Types: " + vtname + " as " + rename)
    #     renaming(volume_types=volume_types, rename=rename)
    #     print("------------------------------------------")
    # # init finish
    # print("Info: Init the Envionment finished.Operate volume_types Information.")
    # create volumtypes
    operate_vt_info(sheet=sheet)


def vt_delete(volume_types):
    try:
        cinder = get_cinder_client()
        print("Deleting volume_type: " + volume_types.name)
        cinder.volume_types.delete(volume_type=volume_types)
        return 1
    except Exception as e:
        print(e.message)
        return 0


# def volume_retype(volumes):
#     try:
#         volumes.retype()
#     except Exception as e:
#         print(e.message)


def renaming(volume_types, rename):
    try:
        cinder = get_cinder_client()
        cinder.volume_types.update(volume_type=volume_types, name=rename)
        return 1
    except Exception as e:
        print("Error: Something wrong when renaming volume_types:" + volume_types.name)
        print(e.message)
        return 0


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


def operate_vt_info(sheet):
    for row in range(1, sheet.nrows):
        vt_name = sheet.cell_value(row, 0)
        backend_name = sheet.cell_value(row, 1)
        # create volumetypes
        print("Info: Create volume_type:"+vt_name+"..Waiting")
        try:
            volumetype = create_volume_types(name=vt_name)
            print("Info: Create volumeType:"+ vt_name + "success")
        except Exception as e:
            print("Error: Create volume_Type:" + vt_name+ "failed. Please check")
            print(e.message)
            continue
        # config metadata
        try:
            volumetype = config_service_spec(vt=volumetype, backend_name=backend_name)
            print("Info: Config metadata:"+ vt_name + "success")
        except Exception as e:
            print("Error: Config metadata:" + vt_name+"failed. Please check")
            print(e.message)


def create_volume_types(name):
    cinder = get_cinder_client()
    volume_types = cinder.volume_types.create(name=name)
    return volume_types


def config_service_spec(vt, backend_name):
    # add ceph as rbd back_end
    print("Info: Set metadata:SERVICE")
    vt = set_metadata(vt, "volume_backend_name", backend_name)
    return vt


def set_metadata(vt, key, value):
    metadata = {key: value}
    return vt.set_keys(metadata=metadata)


if __name__ == '__main__':
    sys.exit(main())



