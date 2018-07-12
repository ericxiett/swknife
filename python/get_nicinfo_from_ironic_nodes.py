# Parse detailed info of nodes in ironic
# Output human format

# Valid fields of nic
import json

import xlwt

VALID_FEILDS = ['index', 'sn', 'name', 'linked', 'mac']
# VALID_FEILDS = ['sn', 'name', 'linked', 'mac', 'vlanid', 'switch', 'port']

import sys

from ironicclient import client


def get_ironic_client():
    args = {
        'token': 'noauth',
        'endpoint': 'http://127.0.0.1:6385',
        'os_ironic_api_version': '1.22',
        'max_retries': 30,
        'retry_interval': 2
    }
    return client.Client(1, **args)


def main():

    style0 = xlwt.easyxf('font: name Times New Roman, bold on;'
                         'borders: left thin, right thin, top thin, bottom thin;',
                         num_format_str='#,##0.00')
    style1 = xlwt.easyxf('font: name Times New Roman;'
                         'borders: left thin, right thin, top thin, bottom thin;')
    wb = xlwt.Workbook()
    ws = wb.add_sheet('nics info')
    for col in range(len(VALID_FEILDS)):
        ws.write(0, col, VALID_FEILDS[col], style0)

    icli = get_ironic_client()
    node_list = icli.node.list()
    row = 1
    for node in node_list:
        node_info = icli.node.get(node.uuid)
        sn = node_info.extra['serial_number']
        nics = node_info.extra['nic_detailed']
        top_row = row
        for nic in nics:
            ws.write(row, VALID_FEILDS.index('index'), row, style1)
            ws.write(row, VALID_FEILDS.index('name'), nic['name'], style1)
            ws.write(row, VALID_FEILDS.index('linked'), nic['has_carrier'], style1)
            ws.write(row, VALID_FEILDS.index('mac'), nic['mac_address'], style1)
            row += 1
        ws.write_merge(top_row, row-1, VALID_FEILDS.index('sn'), VALID_FEILDS.index('sn'), sn, style1)

    wb.save('nics_info.xls')
    print('Get nics info and output nics_info.xls successfully!')


if __name__ == '__main__':
    sys.exit(main())
