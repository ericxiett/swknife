import random
import string
import sys
import time

from keystoneauth1 import loading, session

# Global variables
from novaclient import client

AUTH_URL = 'http://10.10.10.20:35357/v3'
USERNAME = 'ptest'
PASSWORD = 'ptest'
PROJECT_NAME = 'ptest'
DOMAIN_NAME = 'Default'
VERSION = '2.53'

DEFAULT_TIMES = 1
DEFAULT_INTERVAL = 10


def get_nova_client():
    loader = loading.get_plugin_loader('password')
    auth = loader.load_from_options(auth_url=AUTH_URL,
                                    username=USERNAME,
                                    password=PASSWORD,
                                    project_name=PROJECT_NAME,
                                    user_domain_name=DOMAIN_NAME,
                                    project_domain_name=DOMAIN_NAME)
    sess = session.Session(auth=auth)
    return client.Client(VERSION, session=sess)


def main():
    nc = get_nova_client()

    times = DEFAULT_TIMES
    if len(sys.argv) < 2:
        print('Do not input create times, use default %s' % DEFAULT_TIMES)
    else:
        times = int(sys.argv[1])

    for ti in range(times):
        create_servers(nc)
        time.sleep(DEFAULT_INTERVAL)


def create_servers(nc):
    name = 'ptest-' + ''.join(random.sample(string.ascii_letters + string.digits, 8))
    create_result = nc.servers.create(name=name,
                                      flavor='75ec65af-599f-49e6-81dd-8fb318d9ed66',
                                      image='a049c27c-da2b-4df9-ac20-b6baad6aaeb7',
                                      nics=[{'net-id': 'e0e6c9c2-f5e1-47af-a0e7-a22883592c39'}],
                                      max_count=10)
    print('result: ', create_result)
    servers = nc.servers.list(search_opts={'name': name + '*'})
    for server in servers:
        print('Check server %s status' % server.name)
        while True:
            server_info = nc.servers.get(server.id)
            if server_info.status != 'ACTIVE':
                time.sleep(1)
            else:
                print('server %s ACTIVE' % server.name)
                break


if __name__ == '__main__':
    sys.exit(main())
