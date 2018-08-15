#!/usr/bin/env bash

set -ex

salt 'ctl*' cmd.run 'systemctl restart nova-api'
salt 'ctl*' cmd.run 'systemctl restart nova-scheduler'
salt 'ctl*' cmd.run 'systemctl restart nova-conductor'
salt 'ctl*' cmd.run 'systemctl restart nova-consoleauth'
salt 'ctl*' cmd.run 'systemctl restart apache2'
salt 'ctl*' cmd.run 'systemctl restart cinder-scheduler'
salt 'ctl*' cmd.run 'systemctl restart cinder-volume'
salt 'ctl*' cmd.run 'systemctl restart neutron-server'
salt 'ctl*' cmd.run 'systemctl restart glance-api'
salt 'ctl*' cmd.run 'systemctl restart glance-registry'

salt 'gtw*' cmd.run 'systemctl restart neutron-l3-agent'
salt 'gtw*' cmd.run 'systemctl restart neutron-dhcp-agent'
salt 'gtw*' cmd.run 'systemctl restart neutron-metadata-agent'
salt 'gtw*' cmd.run 'systemctl restart neutron-openvswitch-agent'

salt 'cmp*' cmd.run 'systemctl restart neutron-openvswitch-agent'
salt 'cmp*' cmd.run 'systemctl restart neutron-l3-agent'
salt 'cmp*' cmd.run 'systemctl restart neutron-metadata-agent'
salt 'cmp*' cmd.run 'systemctl restart nova-compute'
