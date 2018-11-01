import sys

import xlwt

from keystoneclient.v3 import client as keystonec
from keystoneauth1 import loading, session
from keystoneauth1 import identity
from neutronclient.v2_0 import client as neutronc
from novaclient import client as novac

AUTH_URL = 'http://192.168.2.10:35357/v3'
USERNAME = 'admin'
PASSWORD = '89rqdHLMN5rm0x1P'
PROJECT_NAME = 'admin'
DOMAIN_NAME = 'Default'
DOMAIN_ID = 'default'
VERSION = '2.1'

BACKUP_XLS_FILE = 'backup_chgvr.xls'
UPDATE_XLS_FILE = 'update_router.xls'

VALID_SUBCMD = ['clear', 'add']
VR_FIELDS = ['index', 'project_id', 'project_name', 'router_id', 'router_name', 'extgw_net', 'extgw_port', 'extgw_ip']
FIP_FIELDS = ['index', 'floatingip_addr', 'floatingip_id', 'instance_name', 'instance_uuid']


def get_neutron_client():
    auth = identity.Password(auth_url=AUTH_URL,
                             username=USERNAME,
                             password=PASSWORD,
                             project_name=PROJECT_NAME,
                             project_domain_id=DOMAIN_ID,
                             user_domain_id=DOMAIN_ID)
    sess = session.Session(auth=auth)
    return neutronc.Client(session=sess, endpoint_type='internal')


def get_keystone_client():
    auth = identity.v3.Password(auth_url=AUTH_URL,
                                username=USERNAME,
                                password=PASSWORD,
                                user_domain_id=DOMAIN_ID,
                                project_domain_id=DOMAIN_ID,
                                project_name=PROJECT_NAME)
    sess = session.Session(auth=auth, verify=False)
    return keystonec.Client(session=sess, interface='internal')


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


def get_project_name_by_id(project_id):
    keystone_client = get_keystone_client()
    return keystone_client.projects.get(project_id).name


def get_port_by_ip(ip_addr, net_id):
    neutron_client = get_neutron_client()
    for port in neutron_client.list_ports(network_id=net_id).get('ports'):
        for fixip in port.get('fixed_ips'):
            if fixip.get('ip_address') == ip_addr:
                return port.get('id')

    return None


def get_routers():
    neutron_client = get_neutron_client()
    routers_list = neutron_client.list_routers()
    routers = []
    for rt in routers_list.get('routers'):
        router_id = rt.get('id')
        router_name = rt.get('name')
        if not rt.get('external_gateway_info'):
            print('name %s id %s no external gateway' % (router_name, router_id))
            continue
        project_id = rt.get('project_id')
        project_name = get_project_name_by_id(project_id)
        extgw_net = rt.get('external_gateway_info').get('network_id')
        extgw_ip = rt.get('external_gateway_info').get('external_fixed_ips')[0].get('ip_address')
        extgw_port = get_port_by_ip(extgw_ip, extgw_net)
        print('project %s router %s gwip %s port %s' % (project_name, router_name, extgw_ip, extgw_port))

        routers.append({
            'project_id': project_id,
            'project_name': project_name,
            'router_id': router_id,
            'router_name': router_name,
            'extgw_net': extgw_net,
            'extgw_port': extgw_port,
            'extgw_ip': extgw_ip
        })

    return routers


def get_instance_by_fixip(fixip, fip_addr):
    nova_client = get_nova_client()
    instances = nova_client.servers.list(search_opts={'all_tenants': True})
    for vm in instances:
        addrs = []
        if vm.addresses:
            for key, value in vm.addresses.items():
                for ad in value:
                    addrs.append(ad.get('addr'))
        if fixip in addrs and fip_addr in addrs:
            return vm.name, vm.id

    return None, None


def get_floatingips():
    neutron_client = get_neutron_client()
    floatingips = []
    for floatingip in neutron_client.list_floatingips().get('floatingips'):
        floating_ip_address = floatingip.get('floating_ip_address')
        fixed_ip_address = floatingip.get('fixed_ip_address')
        floatingip_id = floatingip.get('id')

        # If have fixed_ip, the floating ip is associate to instance. Need to record
        instance_name = None
        instance_uuid = None
        if fixed_ip_address:
            instance_name, instance_uuid = get_instance_by_fixip(
                fixed_ip_address, floating_ip_address)

        floatingips.append({
            'floating_ip_address': floating_ip_address,
            'floatingip_id': floatingip_id,
            'instance_name': instance_name,
            'instance_uuid': instance_uuid
        })

        print('floating ip %s instance %s' % (floating_ip_address, instance_name))

    return floatingips


def clear_floatingips(floatingips):
    nova_client = get_nova_client()
    for floatingip in floatingips:
        instance_uuid = floatingip.get('instance_uuid')
        fip_addr = floatingip.get('floating_ip_address')
        server_info = nova_client.servers.get(instance_uuid)
        if not server_info:
            print('No found the %s instance.' % instance_uuid)
        else:
            # api version 2.1
            server_info.remove_floating_ip(fip_addr)
            print('server add floatingip: %s' % fip_addr)


def clear_routers_extgw(routers):
    neutron_client = get_neutron_client()
    for vrid in routers:
        body = {'external_gateway_info': {}}
        neutron_client.update_router(vrid, body)


def build_routers_sheet(routers):
    style0 = xlwt.easyxf('font: name Times New Roman, color-index green, bold on',
                         num_format_str='#,##0')
    style1 = xlwt.easyxf('font: name Times New Roman, color-index black',
                         num_format_str='#,##0')

    wb = xlwt.Workbook()
    ws = wb.add_sheet('routers')

    for col in range(len(VR_FIELDS)):
        ws.write(0, col, VR_FIELDS[col], style0)

    index = 1
    for vr in routers:
        ws.write(index, 0, index, style1)
        ws.write(index, 1, vr.get('project_id'), style1)
        ws.write(index, 2, vr.get('project_name'), style1)
        ws.write(index, 3, vr.get('router_id'), style1)
        ws.write(index, 4, vr.get('router_name'), style1)
        ws.write(index, 5, vr.get('extgw_net'), style1)
        ws.write(index, 6, vr.get('extgw_port'), style1)
        ws.write(index, 7, vr.get('extgw_ip'), style1)
        index += 1

    wb.save(BACKUP_XLS_FILE)


def build_floatingips_sheet(floatingips):
    style0 = xlwt.easyxf('font: name Times New Roman, color-index green, bold on',
                         num_format_str='#,##0')
    style1 = xlwt.easyxf('font: name Times New Roman, color-index black',
                         num_format_str='#,##0')

    wb = xlwt.Workbook()
    ws = wb.add_sheet('floatingips')

    for col in range(len(FIP_FIELDS)):
        ws.write(0, col, FIP_FIELDS[col], style0)

    index = 1
    for fip in floatingips:
        ws.write(index, 0, index, style1)
        ws.write(index, 1, fip.get('floating_ip_address'), style1)
        ws.write(index, 2, fip.get('floatingip_id'), style1)
        ws.write(index, 3, fip.get('instance_name'), style1)
        ws.write(index, 4, fip.get('instance_uuid'), style1)
        index += 1

    wb.save(BACKUP_XLS_FILE)


def add_routers_extgw(ext_new_net):
    style0 = xlwt.easyxf('font: name Times New Roman, color-index green, bold on',
                         num_format_str='#,##0')
    style1 = xlwt.easyxf('font: name Times New Roman, color-index black',
                         num_format_str='#,##0')

    wb = xlwt.Workbook()
    ws = wb.add_sheet('routers')

    for col in range(len(VR_FIELDS)):
        ws.write(0, col, VR_FIELDS[col], style0)

    routers = get_routers()

    neutron_client = get_neutron_client()
    index = 1
    for vr in routers:
        vr_id = vr.get('router_id')
        body = {
            'router': {
                'external_gateway_info': {
                    'network_id': ext_new_net
                }
            }
        }
        vr_info = neutron_client.update_router(vr_id, body)
        extgw_info = vr_info.get('router').get('external_gateway_info')
        ws.write(index, 0, index, style1)
        ws.write(index, 1, vr_info.get('project_id'), style1)
        project_name = get_project_name_by_id(vr_info.get('project_id'))
        ws.write(index, 2, project_name, style1)
        ws.write(index, 3, vr_info.get('id'), style1)
        ws.write(index, 4, vr_info.get('name'), style1)
        extgw_net = extgw_info.get('network_id')
        ws.write(index, 5, extgw_net, style1)
        extgw_ip = extgw_info.get('external_fixed_ips')[0].get('ip_address')
        extgw_port = get_port_by_ip(extgw_ip, extgw_net)
        ws.write(index, 6, extgw_port, style1)
        ws.write(index, 7, extgw_ip, style1)
        print('project %s router %s gwip %s port %s' % (project_name, vr_info.get('name'), extgw_ip, extgw_port))

    wb.save(UPDATE_XLS_FILE)


def main():
    print('Welcome to use this script to change extgw of vrs...')

    if len(sys.argv) < 2:
        print('Please input subcommand: %s' % VALID_SUBCMD)
        return 1
    elif sys.argv[1] not in VALID_SUBCMD:
        print('Please input valid subcommand: %s' % VALID_SUBCMD)
        return 1
    elif sys.argv[1] == 'add' and len(sys.argv) < 3:
        print('Need external network id for add op')
        return 1

    subcmd = sys.argv[1]

    if subcmd == 'clear':
        routers = get_routers()
        floatingips = get_floatingips()
        build_routers_sheet(routers)
        build_floatingips_sheet(floatingips)
        clear_floatingips(floatingips)
        clear_routers_extgw(routers)
    elif subcmd == 'add':
        ext_new_net = sys.argv[2]
        add_routers_extgw(ext_new_net)


if __name__ == '__main__':
    sys.exit(main())
