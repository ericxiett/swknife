#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import xlrd
import xlwt
import os
from keystoneauth1 import loading, session
from novaclient import client as novac

AUTH_URL = ''
USERNAME = 'admin'
PASSWORD = ''
PROJECT_NAME = 'admin'
DOMAIN_NAME = 'Default'
DOMAIN_ID = 'default'
VERSION = '2.26'

OUTPUT_FILE = "tags_input_model.xls"


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


def get_all_servers(nova_client, name=None, detailed=False, use_all=True):
    all_servers = []

    opts = {
        "all_tenants": use_all,
    }

    if name:
        opts.update({"name": name})

    last = None
    while True:
        servers = nova_client.servers.list(detailed=detailed, search_opts=opts,
                                           marker=last.id if last else None)
        if len(servers) == 0:
            break
        all_servers.extend(servers)
        last = all_servers[-1]
    return all_servers


def main():
    print('Welcome to use this script to get all servers tag info...')
    client = get_nova_client()

    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet("servers")
    tittle = ['id', 'service', 'name']

    for i in range(len(tittle)):
        sheet.write(0, i, tittle[i])

    servers = get_all_servers(client)
    index = 1
    for server in servers:
        tags = client.servers.tag_list(server)
        tagstr = ""
        if len(tags) > 0:
            tagstr = tags[0]
        print "id:" + server.id + "  name:" + server.name + "  tag:" + tagstr
        array = [server.id, tagstr, server.name]
        for j in range(len(tittle)):
            sheet.write(index, j, array[j])
        index += 1

    workbook.save(OUTPUT_FILE)


if __name__ == '__main__':
    sys.exit(main())
