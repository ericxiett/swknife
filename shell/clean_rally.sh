#!/bin/bash
#set -e

SOURCE_FILE="/root/keystonercv3"

if  [ ! -e $SOURCE_FILE  ]; then
   echo "$SOURCE_FILE does not exists"
   exit 1
fi


source $SOURCE_FILE

function clear_vms {
    vms=`openstack server list --all-projects | sed -ne '4,$p' | head -n -1 | egrep rally | cut -d'|' -f2`
    for vm in $vms; do
        echo $vm
        openstack server delete $vm
    done
}

function clear_network {
    list=$(openstack network list --project '' | sed -ne '4,$p' | head -n -1 | egrep 'rally' | cut -d'|' -f2)
    for net in $list; do
        echo $net
        ports=$(openstack port list --net $net -f value -c ID)
        for port in $ports; do
            device_id=$(openstack port show $port | grep device_id | cut -d'|' -f3)
            device_owner=$(openstack port show $port | grep device_owner | cut -d'|' -f3)
            echo "port: $port"
            if [[ "${device_owner}" = *"router_centralized_snat"*  ]]; then
                echo "${device_id//[[:space:]]/}, $device_owner"
                openstack router remove port "${device_id//[[:space:]]/}" "${port}"
            fi
        done

        for port in $ports; do
            device_id=$(openstack port show $port | grep device_id | cut -d'|' -f3)
            device_owner=$(openstack port show $port | grep device_owner | cut -d'|' -f3)
            echo "port: $port"
            if [[ "${device_owner}" = *"router_interface_distributed"*  ]]; then
                echo "${device_id//[[:space:]]/}, $device_owner"
                openstack router remove port "${device_id//[[:space:]]/}" "${port}"
            elif [[ "${device_owner}" = *"floating"* ]]; then
                openstack floating ip delete ${device_id}
            else
                openstack port delete $port
            fi
        done
        subnets=$(openstack subnet list --net $net -f value -c ID)
        for subnet in $subnets; do
            echo $subnet
            openstack subnet delete $subnet
        done
        openstack network delete $net
    done
}

function clear_router {
    list=$(openstack router list --project '' | sed -ne '4,$p' | head -n -1 | egrep 'rally' | cut -d'|' -f2)
    for router in $list; do
        echo $router
        openstack router delete $router
    done
}


function clear_projects {
    projects=$(openstack project list | egrep 'rally' | cut -d'|' -f3)
    for project in $projects; do
        echo $project
        openstack project delete $project
    done
}

function clear_user {
    users=$(openstack user list | egrep 'rally' | cut -d'|' -f3)
    for user in $users; do
        echo $user
        openstack user delete $user
    done
}

clear_vms
clear_network
clear_router
clear_projects
clear_user
