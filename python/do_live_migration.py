#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import xlrd
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

INPUT_FILE = "move_instance.xlsx"


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


def main():
    # read config file
    if os.path.exists(INPUT_FILE):
        readbook = xlrd.open_workbook(INPUT_FILE)
        rsheet = readbook.sheet_by_name('Sheet1')
        print "Config file is existed."
    else:
        print("Error: Live migration file '" + INPUT_FILE + "'is not existed.")

    novaclient = get_nova_client()
    print "do live migrate."
    success = []
    failed = []
    shutdown = []
    for row in range(rsheet.nrows):
        try:
            servername = rsheet.cell_value(row, 0)
            serverid = rsheet.cell_value(row, 1)
            source = rsheet.cell_value(row, 3)
            dest = rsheet.cell_value(row, 4)
            server = Server(id=serverid, name=servername)
            server = novaclient.servers.get(server)
            if server.status == "ACTIVE":
                print "Info:  Live migrate server:" + serverid + " from " + source + " to " + dest
                server.live_migrate(host=dest, force=True)
                time.sleep(120)
                print "SUCCESS"
                success.append(serverid)
            else:
                shutdown.append(serverid)
                print "Error:  Server " + serverid + " is not Active"

            print "---------------------------------------------------"
        except Exception as e:
            failed.append(serverid)
            print("Error: Operate server:"+serverid+" Failed.Please check.")
            print e.message
            continue
    print "##############################################################"
    print "success:"
    print success
    print "failed:"
    print failed
    print "shutdown:"
    print shutdown


if __name__ == '__main__':
    sys.exit(main())
