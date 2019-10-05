import sys
import time

import cinderclient.exceptions as cinderc_exc
from common.os_clients import get_keystone_client\
    , get_nova_client, get_cinder_client, get_neutron_client

EXCLUDE = []

def print_helper():
    print('Welcome to use this script!')
    print('This script is used to clean cloud resources.')
    print('Resources include: vm/volume/network/user/project/...')


def clean_neutron_resources(project):
    neutron_client = get_neutron_client()
    # Delete routers
    routers = neutron_client.list_routers()
    for rt in routers:
        ports = neutron_client.list_ports(search_opts={'device_id': rt.id})
        for po in ports:
            neutron_client.delete_port(po.id)
            print('Port %s for router %s deleted' % (po.id, rt.id))
        neutron_client.delete_router(rt.id)
        print('Router %s deleted' % rt.id)


def clean_resources_by_project():
    # Get project list
    keystone_client = get_keystone_client()
    projects = keystone_client.projects.list()

    # Get vm list of project one by one, then delete them
    instance_count = 0
    volume_count = 0
    for pro in projects:
        if pro.name not in EXCLUDE:
            instance_count = clean_nova_resources(pro, instance_count)
            volume_count = clean_cinder_resources(pro, volume_count)
            clean_neutron_resources(pro)

    print('Total %s instances are deleted' % instance_count)
    print('Total %s volumes are deleted' % volume_count)


def clean_cinder_resources(project, count):
    cinder_client = get_cinder_client()
    print('Get volumes of project %s' % project.name)
    volumes = cinder_client.volumes.list(
        search_opts={'project_id': project.id, 'all_tenants': True})
    for vol in volumes:
        # Delete snapshots
        snapshots = cinder_client.volume_snapshots.list(
            search_opts={'volume_id': vol.id})
        for snap in snapshots:
            print('Volume snapshot %s is deleted' % snap.name)
            cinder_client.volume_snapshots.delete(snap.id)
            while True:
                try:
                    cinder_client.volume_snapshots.get(snap.id)
                    time.sleep(1)
                except cinderc_exc.NotFound as e:
                    break

        print('Volume %s is deleted' % vol.name)
        cinder_client.volumes.delete(vol.id)
        count += 1
    return count


def clean_nova_resources(project, count):
    # Resources: instance/flavor, flavor not delete
    nova_client = get_nova_client()
    print('Get instances of project %s' % project.name)
    instances = nova_client.servers.list(
        search_opts={'project_id': project.id, 'all_tenants': True})
    for ins in instances:
        print('Instance %s is deleted' % ins.name)
        nova_client.servers.force_delete(ins.id)
        count += 1
    return count


def main():
    print_helper()
    clean_resources_by_project()


if __name__ == '__main__':
    sys.exit(main())