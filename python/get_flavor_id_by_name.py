import sys

import xlrd
import xlwt

from keystoneauth1 import loading, session

# Global variables
from keystoneauth1 import identity
from novaclient import client as novac

AUTH_URL = 'http://10.10.10.10:35357/v3'
USERNAME = 'admin'
PASSWORD = 'admin'
PROJECT_NAME = 'admin'
DOMAIN_NAME = 'Default'
DOMAIN_ID = 'default'
VERSION = '2.53'

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

def get_id_by_name(flavors):
    xls_file = 'images_flavors.xls'
    wb = xlrd.open_workbook(xls_file)
    # img_sheet = wb.sheet_by_name('images')
    flv_sheet = wb.sheet_by_name('flavors')
    needs = {}
    for row in range(1, flv_sheet.nrows):
        val = flv_sheet.cell_value(row, 1)
        if not val:
            print("val: %s" % val)
            needs[val] = []
            for flv in flavors:
                if flv.name == val:
                    print('Bingo, name %s get id %s' % (val, flv.id))
                    needs[val].append(flv.id)
    return needs


def get_all_flavors():
    nova_client = get_nova_client()
    all_flavors = []
    last = None
    while True:
        flavors = nova_client.flavors.list(marker=last.id if last else None)
        if len(flavors) == 0:
            break
        all_flavors.extend(flavors)
        last = all_flavors[-1]
        print("last flavor is : %s" % last)
    return all_flavors


def output_to_excel(records):
    workboot = xlwt.Workbook()
    wsheet = workboot.add_sheet("cks_flavors")
    tittles = ["name", "id", "count"]
    for i in range(len(tittles)):
        wsheet.write(0, i, tittles[i])
    row = 1
    for key,value in records.items():
        wsheet.write(row, 0, key)
        wsheet.write(row, 1, value)
        wsheet.write(row, 2, len(value))
        row += 1

    workboot.save('cks.xls')


def main():
    '''
    Main steps:
    1. Get all flavors by nova flavor api
    2. Parse names from excel and get id from 1's list
    3. Judge if multiple and output to excel
    '''
    print('Get flavor id by name...')

    flavors = get_all_flavors()
    records = get_id_by_name(flavors)
    output_to_excel(records)


if __name__ == '__main__':
    sys.exit(main())
