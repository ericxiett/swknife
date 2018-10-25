import random
import string
import sys
import time

import xlwt
from keystoneauth1 import loading, session

# Global variables
from novaclient import client

AUTH_URL = 'http://192.168.2.10:35357/v3'
USERNAME = 'xiett'
PASSWORD = 'xiett'
PROJECT_NAME = 'xiett'
DOMAIN_NAME = 'Default'
DOMAIN_ID = 'default'
VERSION = '2.1'
DEFAULT_INTERVAL = 1
DEFAULT_TIMES = 1
XLS_FILE = 'instances.xls'
VALID_FEILDS = ['server_uuid', 'server_name', 'fix_ip', 'floating_ip', 'project']

def get_nova_client():
    loader = loading.get_plugin_loader('password')
    auth = loader.load_from_options(auth_url=AUTH_URL,
                                    username=USERNAME,
                                    password=PASSWORD,
                                    project_name=PROJECT_NAME,
                                    user_domain_name=DOMAIN_NAME,
                                    project_domain_name=DOMAIN_NAME)
    sess = session.Session(auth=auth)
    return client.Client(VERSION, session=sess)


def main():
    nc = get_nova_client()

    times = DEFAULT_TIMES
    if len(sys.argv) < 2:
        print('Do not input create times, use default %s' % DEFAULT_TIMES)
    else:
        times = int(sys.argv[1])

    for ti in range(times):
        create_servers(nc)
        time.sleep(DEFAULT_INTERVAL)


def write_record_to_excel(server_id):
    style0 = xlwt.easyxf('font: name Times New Roman, bold on;'
                         'borders: left thin, right thin, top thin, bottom thin;',
                         num_format_str='#,##0.00')
    style1 = xlwt.easyxf('font: name Times New Roman;'
                         'borders: left thin, right thin, top thin, bottom thin;')
    wb = xlwt.Workbook()
    ws = wb.add_sheet('instances')
    for col in range(len(VALID_FEILDS)):
        ws.write(0, col, VALID_FEILDS[col], style0)


def create_servers(nc):
    name = 'btest-' + ''.join(random.sample(string.ascii_letters + string.digits, 8))
    nc.servers.create(name=name,
                      flavor='48520c32-be48-42ee-8bf4-f17b3e80069c',
                      image='9bedcbbd-492f-4bd9-9221-84165a0d2e47',
                      nics=[{'net-id': '7b01990e-5a7a-481c-8aa9-70e002cfc34d'}],
                      max_count=10)
    style0 = xlwt.easyxf('font: name Times New Roman, bold on;'
                         'borders: left thin, right thin, top thin, bottom thin;',
                         num_format_str='#,##0.00')
    style1 = xlwt.easyxf('font: name Times New Roman;'
                         'borders: left thin, right thin, top thin, bottom thin;')
    wb = xlwt.Workbook()
    ws = wb.add_sheet('instances')
    for col in range(len(VALID_FEILDS)):
        ws.write(0, col, VALID_FEILDS[col], style0)
    servers = nc.servers.list(search_opts={'name': name + '*'})
    row = 1
    for server in servers:
        print('Check server %s status' % server.name)
        while True:
            server_info = nc.servers.get(server.id)
            if server_info.status != 'ACTIVE':
                time.sleep(1)
            else:
                # Write info to XLS_FILE
                print('server %s ACTIVE' % server.id)
                ws.write(row, 0, server.id, style1)
                row += 1
                break
    wb.save(XLS_FILE)


if __name__ == '__main__':
    sys.exit(main())
