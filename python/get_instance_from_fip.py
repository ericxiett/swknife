import sys

from keystoneauth1 import loading, session

# Global variables
from keystoneauth1 import identity
from neutronclient.v2_0 import client as neutronc
from novaclient import client as novac

FIP_LIST = [
    '1.1.1.1',
    '2.2.2.2',
    '3.3.3.3'
]

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


def get_neutron_client():
    auth = identity.Password(auth_url=AUTH_URL,
                             username=USERNAME,
                             password=PASSWORD,
                             project_name=PROJECT_NAME,
                             project_domain_id=DOMAIN_ID,
                             user_domain_id=DOMAIN_ID)
    sess = session.Session(auth=auth)
    return neutronc.Client(session=sess, endpoint_type='internal')


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
            return vm.name

    return None


def get_instances():
    neutron_client = get_neutron_client()
    ins = []
    for fip in neutron_client.list_floatingips().get('floatingips'):
        if fip.get('floating_ip_address') in FIP_LIST:
            fip_addr = fip.get('floating_ip_address')
            fixip = fip.get('fixed_ip_address')
            print('Got fip %s fix %s' % (fip_addr, fixip))
            instance = get_instance_by_fixip(fixip, fip_addr)
            if not instance:
                print('Can not find instance for fip %s' % fip.get('floating_ip_address'))
            else:
                ins_item = {'name': instance, 'floating ip': fip_addr, 'fix ip': fixip}
                ins.append(ins_item)

    return ins


def main():
    print('Welcome to use this script to get instance by fip...')
    instances = get_instances()
    for ins in instances:
        print ins.get('name'), ins.get('floating ip'), ins.get('fix ip')


if __name__ == '__main__':
    sys.exit(main())
