#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import subprocess,re
import xlrd

from keystoneauth1 import loading, session
from keystoneauth1 import identity
from neutronclient.v2_0 import client as neutronc
from novaclient import client as novac
import string

# Global variables
XLS_FILE = 'HgInformation.xlsx'

AUTH_URL='http://192.168.2.11:35357/v3'
USERNAME = 'admin'
PASSWORD = 'Nc3uLtoJkQzas70I'
PROJECT_NAME = 'admin'
DOMAIN_NAME = 'Default'
DOMAIN_ID = 'default'
VERSION = '2.1'

HOST_LIST = None

def create_aggregate(azName,hgName):
    client = get_nova_client()
    aggregate = client.aggregates.create(name=hgName, availability_zone=azName)
    print "create aggregate: ********************* "
    print aggregate
    return aggregate

def check_host_exist(hostname):
    client = get_nova_client()
    instance = client.servers.find(name='hostname')

def get_all_hosts():
    client = get_nova_client()
    host_list = client.hosts.list()
    print "get all hosts:"
    print host_list
    HOST_LIST = host_list

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

def add_metadata(hg,service,spec):
    client = get_nova_client()
    # add SERVICE
    metadata = {"SERVICE": service}
    information = client.aggregates.set_metadata(aggregate=hg, metadata=metadata)
    print "add metadata: SERVICE"
    print information
    # add SPEC
    metadata = {"SPEC": spec}
    information = client.aggregates.set_metadata(aggregate=hg, metadata=metadata)
    print "add metadata: SPEC"
    print information
    return 1

def do_create():
    book = xlrd.open_workbook(XLS_FILE)
    sh = book.sheet_by_name('Sheet1')
    # First column is servers' uuid
    for row in range(2, sh.nrows):
        service_name = sh.cell_value(row, 0)
        az_name = sh.cell_value(row, 1)
        hosts = sh.cell_value(row, 3)
        spec = sh.cell_value(row, 5)

        hgname = az_name + '_' + service_name.lower() + '_' + spec.lower()
        # create host aggregate
        aggregate = create_aggregate(azName=az_name, hgName=hgname)
        #add metadata
        result = add_metadata(hg=aggregate, service=service_name, spec=spec)
        if result:
            print "add metadata success."
            # add host
            number = string.count(hosts)
            if hosts[string._long] == ',':
                number = number - 1
            client = get_nova_client()
            hostList = hosts.split(str=",", num=number)
            for hostname in hostList:
                # check if hosts is existed.
                # **************************#
                # add host
                print "add host:"+hostname
                client.aggregates.add_host(aggregate, hostname)
                print  "****************************"
        else:
            print "add metadata failed."
            return 0

def main():
    print('Welcome to use this script to attach fip on instances...')

    # if len(sys.argv) < 2 or sys.argv[1] not in VALID_SUBCOMMANDS:
    #     print('Please input valid subcommand: attach/restore')
    #     exit(1)
    #
    # subcommand = sys.argv[1]
    do_create()


if __name__ == '__main__':
    sys.exit(main())
