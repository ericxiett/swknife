import sys

import xlwt

from python.common.os_clients import get_nova_client, get_keystone_client, get_glance_client

FIELDS = ['index', 'vm_uuid', 'vm_name', 'status','user','project', 'image', 'addresses']


class RequiredInstanceInfo(object):

    def __init__(self, instance):
        self.uuid = instance.id
        self.name = instance.name
        self.status = instance.status
        self.user = self._get_username_by_id(instance.user_id)
        self.project = self._get_project_name_by_id(instance.tenant_id)
        self.image = self._get_image_name_by_id(instance.image.get('id'))
        self.addresses = instance.addresses

    def _get_username_by_id(self, user_id):
        kc = get_keystone_client()
        user_info = kc.users.get(user_id)
        return user_info.name

    def _get_project_name_by_id(self, tenant_id):
        kc = get_keystone_client()
        project_info = kc.projects.get(tenant_id)
        return project_info.name

    def _get_image_name_by_id(self, image_id):
        gc = get_glance_client()
        image_info = gc.images.get(image_id)
        return image_info.name


def get_all_vms():
    novac = get_nova_client()
    vms_list = []
    instances = novac.servers.list(
        search_opts={'all_tenants': True}, detailed=True)
    for ins in instances:
        vms_list.append(RequiredInstanceInfo(ins))
    while True:
        instances = novac.servers.list(
            search_opts={'all_tenants': True}, detailed=True,
            marker=instances[-1]
        )
        if not instances:
            break
        for ins in instances:
            vms_list.append(RequiredInstanceInfo(ins))

    return vms_list


def export_to_excel(vms_list):
    style0 = xlwt.easyxf('font: name Times New Roman, color-index green, bold on',
                         num_format_str='#,##0')
    style1 = xlwt.easyxf('font: name Times New Roman, color-index black',
                         num_format_str='#,##0')

    wb = xlwt.Workbook()
    ws = wb.add_sheet('all_instances')

    # First row
    for col in range(len(FIELDS)):
        ws.write(0, col, FIELDS[col], style0)

    row = 1
    for vminfo in vms_list:
        ws.write(row, 0, row, style1)
        ws.write(row, 1, vminfo.uuid, style1)
        ws.write(row, 2, vminfo.name, style1)
        ws.write(row, 3, vminfo.status, style1)
        ws.write(row, 4, vminfo.user, style1)
        ws.write(row, 5, vminfo.project, style1)
        ws.write(row, 6, vminfo.image, style1)
        ws.write(row, 7, vminfo.addresses, style1)
        row += 1

    wb.save('all_instances.xls')


def main():
    vms_list = get_all_vms()
    export_to_excel(vms_list)


if __name__ == '__main__':
    sys.exit(main())
