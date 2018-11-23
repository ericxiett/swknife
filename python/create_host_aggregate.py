#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import xlrd
import os
from keystoneauth1 import loading, session
from novaclient import client as novac

# Global variables
# XLS_FILE = 'HgInformation.xlsx'

AUTH_URL = 'http://192.168.2.11:35357/v3'
USERNAME = 'admin'
PASSWORD = '89rqdHLMN5rm0x1P'
PROJECT_NAME = 'admin'
DOMAIN_NAME = 'Default'
DOMAIN_ID = 'default'
VERSION = '2.1'

ERROR_CREATE = "Create Hg Failed."
ERROR_METADATA = "Set Metadata Failed."
ERROR_HOST = "Add Host Failed:"
ERROR_DELETE = "Delete Hg failed."
STATUS_SUCCESS = "SUCCESS"
STATUS_FAILED = "FAILED"
STATUS_HOST_ERROR = "HOST ERROR"

def create_aggregate(azName, hgName):
    NovaClient = get_nova_client()
    aggregate = NovaClient.aggregates.create(name=hgName, availability_zone=azName)
    return aggregate


def check_host_exist(hostname):
    NovaClient = get_nova_client()
    instance = NovaClient.servers.find(name='hostname')


def get_all_hosts():
    NovaClient = get_nova_client()
    host_list = NovaClient.hosts.list()
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


def config_service_spec(hg, service, spec):
    # add SERVICE
    print "Info: Set metadata: SERVICE"
    hg = set_metadata(hg, "SERVICE", service)
    # add SPEC
    print "Info: Set metadata: SPEC"
    hg = set_metadata(hg, "SPEC", spec)
    return hg


def set_metadata(hg, key, value):
    metadata = {key: value}
    NovaClient = get_nova_client()
    return NovaClient.aggregates.set_metadata(aggregate=hg, metadata=metadata)


def init_check(XLS_FILE):
    # read config file
    if os.path.exists(XLS_FILE):
        book = xlrd.open_workbook(XLS_FILE)
        sheet = book.sheet_by_name('Sheet1')
    else:
        print("Error: Host aggregate configation file '" + XLS_FILE + "'is not existed.")
        return 0
    # get the nova client
    NovaClient = get_nova_client()

    # get all old Hgs
    HgList = NovaClient.aggregates.list()
    # delete all Hgs
    for aggregate in HgList:
        hgName = aggregate.name
        print("Warning: Deleting Hg:" + hgName)
        remove_and_delete(aggregate=aggregate)
        print("----------------------------")
    # init finish
    print("Info: Init the Envionment finished.Operate Hg Information.")
    # do operate.
    operate_hg_info(sheet=sheet)

def operate_hg_info(sheet):
    # information result
    result = []
    # check every row
    NovaClient = get_nova_client()
    for row in range(2, sheet.nrows):
        service_name = sheet.cell_value(row, 0)
        az_name = sheet.cell_value(row, 1)
        hosts = sheet.cell_value(row, 2)
        spec = sheet.cell_value(row, 4)
        hgname = az_name + '_' + service_name.lower() + '_' + spec.lower()
        status = STATUS_SUCCESS
        failedhosts = []
        error = []
        hgInfo = {"hgname": hgname, "status": status, "error": error, "failedHost": failedhosts}
        # create host aggregate
        print("Info: Creating Hg:"+hgname+". Waiting.")
        try:
            aggregate = create_aggregate(azName=az_name, hgName=hgname)
            print("Info: Create Hg:" + hgname + "success.")
        except Exception as e:
            print("Error: Create Hg:" + hgname + " for service:" + service_name + " failed.Please check.")
            status = STATUS_FAILED
            error.append(ERROR_CREATE)
            hgInfo.update({
                "status": status,
                "error": error
            })
            result.append(hgInfo)
            print e.message
            continue
        # config metadata
        try:
            aggregate = config_service_spec(hg=aggregate, service=service_name, spec=spec)
            print "Info: Add metadata success."
        except Exception as e:
            print "Error: Set metadata for Hg:" + hgname + " for service:" + service_name + " failed.Please check."
            status = STATUS_FAILED
            error.append(ERROR_METADATA)
            if remove_and_delete(aggregate) == 0:
                error.append(ERROR_DELETE)
            hgInfo.update({
                "status": status,
                "error": error
            })
            result.append(hgInfo)
            print e.message
            continue
        # add host
        hostList = hosts.split(",")
        for hostname in hostList:
            try:
                if len(hostname) > 0:
                    NovaClient.aggregates.add_host(aggregate, hostname)
                    print "Info: Add host:" + hostname + " for Hg:" + hgname + " success."
                    print "****************************"
            except Exception as e:
                print "Error: Add host:" + hostname + "for Hg:" + hgname + " failed."
                status = STATUS_HOST_ERROR
                failedhosts.append(hgname)
                error.append(ERROR_HOST + hostname)
        hgInfo.update({
            "status": status,
            "error": error,
            "failedHost": failedhosts
        })
        result.append(hgInfo)
        # create & set metadata & add hosts SUCCESS.
    # output result.
    output(result=result)


def output(result):
    print("\n")
    print("Operation is Finish.")
    for hgInfo in result:
        print("----------------------------")
        print("HgName: " + hgInfo.get("hgname"))
        status = hgInfo.get("status")
        print("Status: " + status)
        if status != STATUS_SUCCESS:
            errors = hgInfo.get('error')
            print("Errors:")
            for error in errors:
                print("   *" + error)
            if status == STATUS_HOST_ERROR:
                print("Failed hosts:")
                index = 0
                hosts = hgInfo.get('failedHost')
                for failedhost in hosts:
                    print("   ")
                    print(failedhost)
                    index += 1
                    if index % 5 == 0:
                        print("\n")


def remove_and_delete(aggregate):
    try:
        hosts = aggregate.hosts
        NovaClient = get_nova_client()
        # if the Hg has hosts,remove them.
        if len(hosts) > 0:
            for hostname in hosts:
                print("Warning: Remove host:"+hostname+" from Hg:"+aggregate.name)
                NovaClient.aggregates.remove_host(aggregate=aggregate, host=hostname)

        # delete Hg
        print("Warning: Delete Hg:" + aggregate.name)
        NovaClient.aggregates.delete(aggregate=aggregate)
        return 1
    except Exception as e:
        print ("Error: Something wrong when remove hosts and delete Hg:" + aggregate.name)
        print e.message
        return 0


def main():
    print('Welcome to use this script to create host aggregates...')
    if len(sys.argv) < 2:
        print('Please input valid the path of HgInformationFile.')
        exit(1)
    XLS_FILE = sys.argv[1]
    init_check(XLS_FILE=XLS_FILE)


if __name__ == '__main__':
    sys.exit(main())
