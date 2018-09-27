import sys

from netmiko import ConnectHandler

# Global info
IP_SW = '10.110.25.250'
USER_NAME = 'qiqianqian'
PASSWORD = 'qiqianqian'

VLANS_NEED_ADDED = [
    {
        'vlanid': '201',
        'netmask': '255.255.255.0',
        'gateway': '192.168.11.254'
    },
    {
        'vlanid': '202',
        'netmask': '255.255.255.0',
        'gateway': '192.168.12.254'
    }
]

PORTS_NEED_CONFED = [
    'GigabitEthernet1/0/6',
    'GigabitEthernet1/0/7',
    'GigabitEthernet1/0/8',
    'GigabitEthernet1/0/9',
    'GigabitEthernet1/0/3',
]


def add_vlan(conn, vlan):
    print('Add vlan %s', vlan.get('vlanid'))

    vlanid = vlan.get('vlanid')
    conn.send_command('vlan ' + vlan.get('vlanid'),
                      expect_string="[poc test-vlan" + vlanid + "]", max_loops=10)
    conn.send_command('quit', expect_string="[poc test]", max_loops=10)


def permit_vlan_to_port(conn, port, vlan):
    print('Permit vlan %s to port %s' % (vlan.get('vlanid'), port))

    vlanid = vlan.get('vlanid')
    conn.send_command('interface ' + port,
                      expect_string=port,
                      max_loops=10)
    conn.send_command('port trunk permit vlan ' + vlanid,
                      expect_string=port,
                      max_loops=10)
    conn.send_command('quit', expect_string="[poc test]", max_loops=10)


def config_ip_addr(conn, vlan):
    print('Config ip addr for %s' % vlan.get('vlanid'))

    vlanid = vlan.get('vlanid')

    conn.send_command('interface Vlan-interface ' + vlan.get('vlanid'),
                      expect_string=vlanid,
                      max_loops=10)
    conn.send_command('ip address ' + vlan.get('gateway') + ' '
                      + vlan.get('netmask'),
                      expect_string=vlanid,
                      max_loops=10)
    conn.send_command('quit', expect_string="[poc test]", max_loops=10)

def main():
    print('Welcome to use this script for configuring H3C SW...')
    print('Please install netmiko firstly!')

    h3c_sw = {
        'device_type': 'huawei',
        'ip': IP_SW,
        'username': USER_NAME,
        'password': PASSWORD
    }

    net_connect = ConnectHandler(**h3c_sw)
    print('[dbg]prompt: %s' % net_connect.find_prompt())

    net_connect.config_mode()
    print('[dbg]prompt: %s' % net_connect.find_prompt())

    # Add vlan
    for vlan in VLANS_NEED_ADDED:
        add_vlan(net_connect, vlan)
        config_ip_addr(net_connect, vlan)
        for port in PORTS_NEED_CONFED:
            permit_vlan_to_port(net_connect, port, vlan)

    net_connect.save_config(cmd='save')


if __name__ == '__main__':
    sys.exit(main())
