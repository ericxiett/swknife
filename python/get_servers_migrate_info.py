#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import xlrd
import xlwt
import os
from keystoneauth1 import loading, session
from novaclient import client as novac
from keystoneauth1.identity import v3
from keystoneclient.v3 import client as keystonec

AUTH_URL = ''
USERNAME = 'admin'
PASSWORD = ''
PROJECT_NAME = 'admin'
DOMAIN_NAME = 'Default'
DOMAIN_ID = 'default'
VERSION = '2.26'

INPUT_FILE = "input.xlsx"
OUTPUT_FILE = "servers_info.xls"


class Server(object):
    available = "active"

    def __init__(self, id, name):
        # this id will not be used if
        # search name returns a list with more than 1 element
        self.id = id
        self.name = name
        # self.service = service
        # self.host = host
        # self.dest = dest
        # self.project_name = project_name
        # self.username = username


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


def get_keystone_client():
    auth = v3.Password(auth_url=AUTH_URL,
                       username=USERNAME,
                       password=PASSWORD,
                       user_domain_id=DOMAIN_ID,
                       project_domain_id=DOMAIN_ID,
                       project_name=PROJECT_NAME)
    sess = session.Session(auth=auth, verify=False)
    return keystonec.Client(session=sess, interface='public')


def get_parse():
    import argparse
    parser = argparse.ArgumentParser(description="parses information:")
    parser.add_argument('-i', '--input', dest='config_path', help='Input server information excel file path.',
                        default=INPUT_FILE)
    parser.add_argument('-o', '--output', dest='output_path', help='Output server information excel file path.',
                        default=OUTPUT_FILE)
    return parser.parse_args()


def main():
    print('Welcome to use this script to get servers  info...')
    parameters = get_parse()
    INPUT_FILE = parameters.config_path
    OUTPUT_FILE = parameters.output_path

    client = get_nova_client()
    workbook = xlwt.Workbook()
    wsheet = workbook.add_sheet("servers")
    wsheet_move = workbook.add_sheet("need moved")
    wsheet_reserve = workbook.add_sheet("reserved")
    tittle = ['name', 'id', 'service', 'host', 'dest', 'project_name', 'user_name', 'other', 'status']

    for i in range(len(tittle)):
        wsheet.write(0, i, tittle[i])
        wsheet_move.write(0, i, tittle[i])
        wsheet_reserve.write(0, i, tittle[i])
    # read config file
    if os.path.exists(INPUT_FILE):
        readbook = xlrd.open_workbook(INPUT_FILE)
        rsheet = readbook.sheet_by_name('Sheet1')
        print "Config file is existed."
    else:
        print("Error: Host aggregate configation file '" + INPUT_FILE + "'is not existed.")

    keystone_client = get_keystone_client()
    # get project info
    print "collecting projects information."
    projects = keystone_client.projects.list(domain=DOMAIN_ID)
    project_dic = {}
    for project in projects:
        project_dic.update({project.id: project.name})
    # get user info
    print "collecting users information."
    users = keystone_client.users.list(domain=DOMAIN_ID)
    user_dic = {}
    for user in users:
        user_dic.update({user.id: user.name})
    # get aggregate info
    hgs = client.aggregates.list()
    reservedHost = []
    beijing1Host = []
    beijing2Host = []
    for hg in hgs:
        hosts = hg.hosts
        # if (hg.id == 43):
        #     for index in range(len(hosts)):
        #         beijing1Host.append(hosts[index])
        # if (hg.id == 46):
        #     for index in range(len(hosts)):
        #         beijing2Host.append(hosts[index])
        if (hg.id == 58):
            for index in range(len(hosts)):
                reservedHost.append(hosts[index])
    print "beijing 1 hosts:"
    print beijing1Host
    print "beijing 2 hosts:"
    print beijing2Host
    print "reserved  hosts:"
    print reservedHost
    print "*********************************************"

    index_move = 1
    idnex_reserve = 1

    for i in range(1, rsheet.nrows):

        name = rsheet.cell_value(i, 0)
        id = rsheet.cell_value(i, 1)
        print "doing: " + id
        # service = rsheet.cell_value(i, 2)
        host = rsheet.cell_value(i, 3)
        # dest = rsheet.cell_value(i, 4)

        server = Server(name=name, id=id)
        server = client.servers.get(server)

        project_id = server.tenant_id
        user_id = server.user_id

        project_name = project_dic.get(project_id)
        username = user_dic.get(user_id)

        for j in range(rsheet.ncols):
            wsheet.write(i, j, rsheet.cell_value(i, j))

        wsheet.write(i, 5, project_name)
        wsheet.write(i, 6, username)

        if (host in reservedHost):
            for j in range(rsheet.ncols):
                wsheet_reserve.write(idnex_reserve, j, rsheet.cell_value(i, j))
            wsheet_reserve.write(idnex_reserve, 5, project_name)
            wsheet_reserve.write(idnex_reserve, 6, username)
            wsheet_reserve.write(idnex_reserve, 8, server.status)
            # if (host in beijing1Host):
            #     print "server " + id + " id in beijing1"
            #     wsheet_reserve.write(idnex_reserve, 7, "beijing1")
            # if (host in beijing2Host):
            #     print "server " + id + " id in beijing2"
            #     wsheet_reserve.write(idnex_reserve, 7, "beijing2")
            if (host in reservedHost):
                print "server " + id + " id in reserved."
                wsheet_reserve.write(idnex_reserve, 7, "reserved")
            idnex_reserve = (idnex_reserve + 1)

        else:
            for j in range(rsheet.ncols):
                wsheet_move.write(index_move, j, rsheet.cell_value(i, j))
            wsheet_move.write(index_move, 5, project_name)
            wsheet_move.write(index_move, 6, username)
            wsheet_move.write(index_move, 8, server.status)
            index_move = (index_move + 1)

        print "____________________________________"

    workbook.save(OUTPUT_FILE)


if __name__ == '__main__':
    sys.exit(main())
