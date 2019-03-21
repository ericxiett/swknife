#!/usr/bin/env bash

set -x

source /root/cert-adminrc

if [[ ! -n "$1" ]]; then
    echo "Empty cmp host!"
    exit
fi
cmphost=$1
sletime=5
for vid in `openstack --insecure server list --all --host $cmphost -f value -c ID`
do

# Stop server
echo "Start stopping $vid"
status_shutoff=`openstack --insecure server show $vid | grep status | grep SHUTOFF`
if [[ ! -n "$status_shutoff" ]];then
openstack --insecure server stop $vid
while true
do
status_shutoff="`openstack --insecure server show $vid | grep status | grep SHUTOFF`"
if [[ -n "$status_shutoff" ]];then
break
fi
sleep $sletime
done
fi


# Migrate server
echo "Start migrating $vid"
openstack --insecure server migrate $vid
while true
do
status_shutoff="`openstack --insecure server show $vid | grep status | grep VERIFY_RESIZE`"
if [[ -n "$status_shutoff" ]];then
break
fi
sleep $sletime
done

# Confirm resize
echo "Start confirming $vid"
openstack --insecure server resize --confirm $vid
while true
do
status_shutoff="`openstack --insecure server show $vid | grep status | grep SHUTOFF`"
if [[ -n "$status_shutoff" ]];then
break
fi
sleep $sletime
done

# Start server
echo "Start starting $vid"
openstack --insecure server start $vid

done

