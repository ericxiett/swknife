import commands
import sys

from ironicclient import client

NEW_USERNAME = 'icpuser'
NEW_PASSWORD = 'xiiGnfLdsx6rw0'

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
    icli = get_ironic_client()
    node_list = icli.node.list()
    for node in node_list:
        node_info = icli.node.get(node.uuid)
        ipmi_addr = node_info.driver_info['ipmi_address']

        cmds = [
            'ipmitool -I lanplus -H ' + ipmi_addr +
            ' -U admin -P admin user set name 10 ' + NEW_USERNAME,
            'ipmitool -I lanplus -H ' + ipmi_addr +
            ' -U admin -P admin user set password 10 ' + NEW_PASSWORD,
            'ipmitool -I lanplus -H ' + ipmi_addr +
            ' -U admin -P admin user enable 10',
            'ipmitool -I lanplus -H ' + ipmi_addr +
            ' -U admin -P admin channel setaccess 1 10 link=on ipmi=on callin=on privilege=4'
        ]

        for cmd in cmds:
            ret = commands.getoutput(cmd)
            print('ret: %s' % ret)

        print('\n')
        user_list = commands.getoutput(
            'ipmitool -I lanplus -H ' + ipmi_addr +
            ' -U admin -P admin user list 1'
        )
        print('user list: \n')
        print(user_list)


if __name__ == '__main__':
    sys.exit(main())
