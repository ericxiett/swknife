#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import xlrd
import xlwt
import time
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

OUTPUT_FILE = "all_flavors.xls"
tittles = ["id", "name", "RAM", "disk", "ephemeral", "vcpus", "is public"]


def get_all_flavors(nova_client):
    print "get all flavors."
    all_flavors = []
    last = None
    while True:
        flavors = nova_client.flavors.list(marker=last.id if last else None)
        if len(flavors) == 0:
            break
        all_flavors.extend(flavors)
        last = all_flavors[-1]
        print "last flavor is :"
        print last
    return all_flavors


def write_flavors_to_excel(flavors):
    print "write flavors to excel file:" + OUTPUT_FILE
    workboot = xlwt.Workbook()
    wsheet = workboot.add_sheet("all flavors")
    # write tittles
    for i in range(len(tittles)):
        wsheet.write(0, i, tittles[i])
    # write flavor info
    write_row = 1
    for flavor in flavors:
        dict = flavor.__dict__
        id = dict.get("id")
        name = dict.get("name")
        ram = dict.get("ram")
        disk = dict.get("disk")
        ephemeral = dict.get("OS-FLV-EXT-DATA:ephemeral")
        vcpus = dict.get("vcpus")
        ispublic = dict.get("os-flavor-access:is_public")

        data = [id, name, ram, disk, ephemeral, vcpus, ispublic]

        for j in range(len(data)):
            wsheet.write(write_row, j, data[j])

        write_row = write_row + 1
    workboot.save(OUTPUT_FILE)


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


def main():
    print "main"
    nova_client = get_nova_client()
    flavors = get_all_flavors(nova_client)
    write_flavors_to_excel(flavors)


if __name__ == '__main__':
    sys.exit(main())
