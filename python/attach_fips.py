#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import subprocess,re

import xlrd
from keystoneauth1 import loading, session

# Global variables
from keystoneauth1 import identity
from neutronclient.v2_0 import client as neutronc
from novaclient import client as novac

VALID_SUBCOMMANDS = ['attach', 'restore']

XLS_FILE = 'instances.xls'
BACKUP_FILE = 'backup.txt'
# FLOATINGIP_NETID = '9c52280d-3b64-4cd0-bbdf-058bd3c42ce9'
FLOATINGIP_NETID = 'd9c00a35-fea8-4162-9de1-b8100494a11d'

AUTH_URL = 'http://192.168.2.10:35357/v3'
USERNAME = 'admin'
PASSWORD = '89rqdHLMN5rm0x1P'
PROJECT_NAME = 'admin'
DOMAIN_NAME = 'Default'
DOMAIN_ID = 'default'
VERSION = '2.1'

def NetCheck(ip):
   try:
    p = subprocess.Popen(["ping -c 3 -W 1 "+ ip],stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    out=p.stdout.read()
    err=p.stderr.read()
    regex_out=re.compile('100% packet loss')
    regex_err=re.compile('unknown host')
    if len(regex_err.findall(err)) == 0:
        if len(regex_out.findall(out)) == 0:
            print ip + ': host up'
            return 'UP'
        else:
            print ip + ': host down'
            return 'DOWN'
    else:
        print ip + ': host unknown please check DNS'
   except:
       print 'NetCheck work error!'
   return 'ERR'

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


def get_neutron_client():
    auth = identity.Password(auth_url=AUTH_URL,
                             username=USERNAME,
                             password=PASSWORD,
                             project_name=PROJECT_NAME,
                             project_domain_id=DOMAIN_ID,
                             user_domain_id=DOMAIN_ID)
    sess = session.Session(auth=auth)
    return neutronc.Client(session=sess, endpoint_type='internal')


def create_floatingipaddr(network_id):
    body = {
        "floatingip": {
            'floating_network_id': network_id
        }
    }
    neutron_client = get_neutron_client()
    fip = neutron_client.create_floatingip(body).get('floatingip')
    fip_address = fip.get('floating_ip_address')
    fip_id = fip.get('id')
    print('The new floating ip created: %s' % fip_address)
    return fip_address, fip_id


def floatingip_to_server(server_uuid, floatingip):
    nova_client = get_nova_client()
    #nova_client.servers.add_floating_ip
    server_info = nova_client.servers.get(server_uuid)
    if not server_info:
        print('No found the %s instance.' % server_uuid)
    else:
        #api version 2.1
        server_info.add_floating_ip(floatingip)
        print('server add floatingip: %s' % floatingip)


def get_instance_by_id(server_id):
    nova_client = get_nova_client()
    instance = nova_client.servers.get(server_id)
    fixed_ips = []
    floating_ips = []
    for key, value in instance.addresses.items():
        for add_id in iter(value):
            if add_id.get('OS-EXT-IPS:type') == 'fixed':
                print('The vm fixed ip is:%s' % add_id.get('addr'))
                fixed_ips.append(add_id.get('addr'))
            else:
                print('The vm floating ip is:%s' % add_id.get('addr'))
                floating_ips.append(add_id.get('addr'))
    return fixed_ips, floating_ips


def attach_fips_to_instances():
    # Get instances provided from haopijia
    book = xlrd.open_workbook(XLS_FILE)
    sh = book.sheet_by_name('instances')
    # First column is servers' uuid
    for row in range(1, sh.nrows):
        ins_uuid = sh.cell_value(row, 0)
        fixed_ips, floating_ips = get_instance_by_id(ins_uuid)

        if len(floating_ips) == 0:
            print('===========')
            # No floating ip, Need to attach one.
            fip_addr, fip_id = create_floatingipaddr(FLOATINGIP_NETID)
            floatingip_to_server(ins_uuid, fip_addr)
            print('===========')
            line = ins_uuid + ' ' + fip_id + ' ' + fip_addr + '\n'
            # Then record this on backup file.
            # And detach it after scanning
            with open('backup.txt', 'a+') as f:
                f.write(line)


def detach_fip(server_uuid, fip_addr):
    nova_client = get_nova_client()
    server_info = nova_client.servers.get(server_uuid)
    if not server_info:
        print('No found the %s instance.' % server_uuid)
    else:
        #api version 2.1
        server_info.remove_floating_ip(fip_addr)
        print('server add floatingip: %s' % fip_addr)


def release_fip(fip_addr):
    neutron_client = get_neutron_client()
    neutron_client.delete_floatingip(fip_addr)
    print('The floating ip %s is deleted' % fip_addr)


def restore_by_backup():
    fip_list = []
    with open(BACKUP_FILE, 'r') as f:
        lines = f.readlines()
        for line in lines:
            server_uuid = line.split(' ')[0]
            fip_id = line.split(' ')[1]
            fip_addr = line.split(' ')[2].strip('\n')
            detach_fip(server_uuid, fip_addr)
            release_fip(fip_id)


def main():
    print('Welcome to use this script to attach fip on instances...')

    if len(sys.argv) < 2 or sys.argv[1] not in VALID_SUBCOMMANDS:
        print('Please input valid subcommand: attach/restore')
        exit(1)

    subcommand = sys.argv[1]

    if subcommand == 'attach':
    # First delete residual files last time
        if os.path.exists(BACKUP_FILE):
            print('Backup file last time need to be deleted!')
            os.remove(BACKUP_FILE)

        try:
            attach_fips_to_instances()
        except Exception as e:
            print('Got error %s' % e)
            exit(1)
    else:
        restore_by_backup()


if __name__ == '__main__':
    sys.exit(main())
