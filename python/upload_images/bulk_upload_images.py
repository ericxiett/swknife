import commands
import os
import sys

import xlrd
import xlwt

from common.os_clients import get_glance_client

FIELDS = ['index', 'name', 'path', 'disk_format', 'properties']

def generate_template():
    print('Starting to generate template...')
    style0 = xlwt.easyxf('font: name Times New Roman, color-index green, bold on',
                         num_format_str='#,##0')

    wb = xlwt.Workbook()
    ws = wb.add_sheet('images_need_to_uploaded')

    # First row
    for col in range(len(FIELDS)):
        ws.write(0, col, FIELDS[col], style0)

    wb.save('upload_images.xls')
    print('Generate template ./upload_images.xls successfully!')
    print('Do not rename xls when uploading template!!!')


def upload_images():
    print('Starting to upload images...')

    # Parse ./upload_images.xls
    if not os.path.exists('upload_images.xls'):
        print('Please upload upload_images.xls to current dir!')
        raise Exception('upload_images.xls does not exist!')

    print('Parse xls...')
    xls_file = 'upload_images.xls'
    wb = xlrd.open_workbook(xls_file)
    sheet = wb.sheet_by_name('images_need_to_uploaded')
    images = []
    for row in range(1, sheet.nrows):
        image = {}
        for col in range(1, sheet.ncols):
            if col > len(FIELDS):
                break
            val = sheet.cell_value(row, col)
            image[FIELDS[col]] = val
        print('\t %s: %s' % (row, image))
        images.append(image)

    print('Upload image...')
    gc = get_glance_client()
    for img in images:
        image_file = img.get('path')
        cmd = 'qemu-img info ' + image_file + ' | grep format'
        cmdout = commands.getoutput(cmd)
        org_format = cmdout.split(':')[1].strip()
        if org_format != 'raw':
            print('%s Not raw format, so convert...' % org_format)
            os.system('qemu-img convert -O raw ' + image_file + ' ' + img.get('name'))

        # upload
        image = gc.images.create(name=img.get('name'),
                                 disk_format='raw',
                                 container_format='public',
                                 )



def main():
    if len(sys.argv) < 2:
        print('Please input valid param: gentpl or upload...')
        exit(1)

    if sys.argv[1] == 'gentpl':
        generate_template()
    elif sys.argv[1] == 'upload':
        upload_images()
    else:
        print('Invalid param %s' % sys.argv[1])
        exit(1)


if __name__ == '__main__':
    sys.exit(main())