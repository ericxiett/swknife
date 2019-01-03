# coding=utf-8
import sys
import time
import xlwt
import time
from keystoneauth1 import loading, session
from cinderclient import client as clientc

AUTH_URL = 'http://10.200.0.20:35357/v3'
USERNAME = 'admin'
PASSWORD = 'vjYXTG6vptMNweIx'
PROJECT_NAME = 'admin'
DOMAIN_NAME = 'Default'
DOMAIN_ID = 'default'
VERSION = '2.1'

VALID_FEILDS = ['ID', 'volumeID', 'volumeName', 'date', 'productTag', 'volumeType']


def get_cinder_client():
    loader = loading.get_plugin_loader('password')
    auth = loader.load_from_options(auth_url=AUTH_URL,
                                    username=USERNAME,
                                    password=PASSWORD,
                                    project_name=PROJECT_NAME,
                                    user_domain_name=DOMAIN_NAME,
                                    project_domain_name=DOMAIN_NAME)
    sess = session.Session(auth=auth)
    return clientc.Client(VERSION, session=sess, endpoint_type='internal')


def main():
    print('welcome to use this scripts to add volume metadata..')
    cinder = get_cinder_client()
    vollist = cinder.volumes.list(search_opts={"all_tenants": True})
    # find out unseted metadata volumes
    vols = volfilter(vollist=vollist)
    # write record to excel
    write_record_to_excel(vols=vols)


def volfilter(vollist):
    print('find out unseted metadata volumes ..')
    try:
        vols = []
        for volume in vollist:
            if volume.metadata:
                md = volume.metadata
                if not md.has_key('productTag'):
                    vols.append(volume)
            else:
                vols.append(volume)
        print("finish volfilter circle.")
        for vol in vols:
            print(vol, vol.volume_type)
        return vols
    except Exception as e:
        print(e.message)


def write_record_to_excel(vols):
    print("start write record to excel......")
    style0 = xlwt.easyxf('font: name Times New Roman, bold on;'
                         'borders: left thin, right thin, top thin, bottom thin;',
                         num_format_str='#,##0.00')
    style1 = xlwt.easyxf('font: name Times New Roman;'
                         'borders: left thin, right thin, top thin, bottom thin;')
    try:
        wb = xlwt.Workbook()
        ws = wb.add_sheet('volumes')
        for col in range(len(VALID_FEILDS)):
            ws.write(0, col, VALID_FEILDS[col], style0)
        print("write titles.....")
        for n, vol in zip(range(len(vols)), vols):
            ws.write(n + 1, 0, int(n + 1), style0)
            ws.write(n + 1, 1, vol.id, style0)
            ws.write(n + 1, 2, vol.name, style0)
            ws.write(n + 1, 3, time.asctime(time.localtime(time.time())), style0)
            ws.write(n + 1, 4, 'productTag=EBS', style0)
            ws.write(n + 1, 5, vol.volume_type, style0)
        wb.save('add_vol_metadata.xls')
    except Exception as e:
        print(e.message)


if __name__ == '__main__':
    sys.exit(main())
