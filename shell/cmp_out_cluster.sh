#!/usr/bin/env bash

set -x

ctl01_name="mf-controller1"
actual_name=`hostname`
if [[ "$actual_name" != "$ctl01_name" ]];then
    echo "Please execute this script on ctl01 node!"
    exit
fi

echo "Start to process on cmp nodes..."
for i in `seq 11 20`
do
# Stop openstack service
ssh root@mf-compute$i systemctl stop openstack-nova-compute
ssh root@mf-compute$i systemctl stop neutron-openvswitch-agent

# Disable openstack service
ssh root@mf-compute$i systemctl disable openstack-nova-compute
ssh root@mf-compute$i systemctl diable neutron-openvswitch-agent

# Remove openstack packages
ssh root@mf-compute$i yum erase -y openstack-nova-compute
ssh root@mf-compute$i yum erase -y neutron-openvswitch-agent
done

sleep 60

echo "Start to clean data about cmp11-20..."
source /root/cert-adminrc
for i in `seq 11 20`
do
# Delete nova-compute service
sid=`openstack --insecure compute service list --host mf-compute$i -f value -c Id`
openstack --insecure compute service delete $sid

# Delete network agents
aid=`neutron --insecure agent-list | grep mf-compute$i | awk -F'|' '{print $2}'`
neutron --insecure agent-delete $aid
done

echo "Results:"
openstack --insecure compute service list
neutron --insecure agent-list
