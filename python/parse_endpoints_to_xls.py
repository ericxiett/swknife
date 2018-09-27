import sys

import xlwt
from keystoneauth1 import session
from keystoneauth1.identity import v3
from keystoneclient.v3 import client

# Global info
AUTH_URL = 'https://10.110.25.117:5000/v3'
USERNAME = 'admin'
PASSWORD = '89rqdHLMN5rm0x1P'
PROJECT_NAME = 'admin'
DOMAIN_ID = 'default'

FIELDS = ['index', 'service', 'port', 'type']

VALID_SERVICES = ['nova', 'cinderv2', 'cinderv3', 'neutron', 'glance', 'keystone', 'ironic']

def get_keystone_client():
    auth = v3.Password(auth_url=AUTH_URL,
                       username=USERNAME,
                       password=PASSWORD,
                       user_domain_id=DOMAIN_ID,
                       project_domain_id=DOMAIN_ID,
                       project_name=PROJECT_NAME)
    sess = session.Session(auth=auth, verify=False)
    return client.Client(session=sess, interface='public')


def get_service_name_by_id(sid, svcs):

    for svc in svcs:
        if svc.id == sid:
            return svc.name

    return None


def build_sheet():
    style0 = xlwt.easyxf('font: name Times New Roman, color-index green, bold on',
                         num_format_str='#,##0')
    style1 = xlwt.easyxf('font: name Times New Roman, color-index black',
                         num_format_str='#,##0')

    wb = xlwt.Workbook()
    ws = wb.add_sheet('ports_in_MCP')

    # First row
    for col in range(len(FIELDS)):
        ws.write(0, col, FIELDS[col], style0)

    return wb, ws, style1


def parse_endpoints(endpoints, services):

    wb, ws, style = build_sheet()

    index = 1
    for endpoint in endpoints:
        # Only public type
        if endpoint.interface == 'public':
            svc_name = get_service_name_by_id(endpoint.service_id, services)
            if svc_name and svc_name in VALID_SERVICES:
                print('[dbg]url: %s' % endpoint.url)
                # url=http://10.110.25.153:8080/swift/v1
                port = endpoint.url.split('/')[2].split(':')[1]
                print('[dbg]port: %s' % port)
                ws.write(index, 0, index, style)
                ws.write(index, 1, svc_name, style)
                ws.write(index, 2, port, style)
                ws.write(index, 3, endpoint.interface, style)

                index += 1

    wb.save('MCP_ports.xls')


def main():
    print('Welcome to use this script')

    try:
        kc = get_keystone_client()
        endpoints = kc.endpoints.list()
        services = kc.services.list()
        parse_endpoints(endpoints, services)
    except Exception as e:
        print('Got exception %s' % e)
        exit(1)


if __name__ == '__main__':
    sys.exit(main())
