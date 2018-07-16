import socket
import sys
import time

import xlrd

from ironicclient import client

WORK_DIR = '/root/'
XLS_FILE = WORK_DIR + 'ipmi_conf.xls'
VALID_FIELDS = ['index', 'sn', 'ipmi_addr', 'ipmi_netmask', 'ipmi_gateway']

def get_ironic_client():
    args = {
        'token': 'noauth',
        'endpoint': 'http://127.0.0.1:6385',
        'os_ironic_api_version': '1.22',
        'max_retries': 30,
        'retry_interval': 2
    }
    return client.Client(1, **args)

def check_conn(address, port):
    sock = socket.socket()
    frequency = 0
    while frequency < 4:
        try:
            sock.connect((address, port))
            print("Connected to %s on port %s" % (address, port))
            return "success"
        except socket.error as e:
            print("Connection to %s on port %s failed: %s,"
                     " already wait: %s s" % (address, port, e, frequency*3))
            frequency += 1
            time.sleep(3)

    return "fail"

def main():
    # Import xls and generate bash script
    book = xlrd.open_workbook(XLS_FILE)
    sh = book.sheet_by_name('ipmi conf')

    for col in range(len(VALID_FIELDS)):
        if sh.cell_value(0, col) != VALID_FIELDS[col]:
            print('Invalid field: ', sh.cell_value(0, col),
                  ', should be ', VALID_FIELDS[col])
            exit(1)

    ipmis = {}
    for row in range(1, sh.nrows):
        confed_sn = str(int(sh.cell_value(row, VALID_FIELDS.index('sn'))))
        confed_addr = str(sh.cell_value(row, VALID_FIELDS.index('ipmi_addr')))
        ipmis[confed_sn] = confed_addr

    icli = get_ironic_client()
    nodes = icli.node.list()
    for node in nodes:
        node_info = icli.node.get(node.uuid)
        sn = node_info.extra['serial_number']
        if sn in ipmis.keys():
            if node_info.driver_info['ipmi_address'] != ipmis[sn]:
                patches = [
                    {
                        'op': 'add',
                        'path': '/driver_info/ipmi_address',
                        'value': ipmis[sn]
                    },
                ]
                icli.node.update(node.uuid, patches)


if __name__ == '__main__':
    sys.exit(main())
