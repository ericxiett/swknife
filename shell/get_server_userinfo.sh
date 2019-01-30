#!/bin/bash
# $* mutil parameters

TIMESTAMP=$(date +%Y%m%d)

check_parameter()
{

	if [ $# -lt 1 ]
    then
        echo -e "Warning:The script must have one parameters."
        echo "#########################################################################"
        echo "Usage: sh $0 serveruuid"

        echo  -e "Example: sh $0 a6c6a683-5419-4ed8-8bfb-69e2c24f269f"
        echo "or"
        echo  -e "Example: sh $0 a6c6a683-5419-4ed8-8bfb-69e2c24f269f 15794036-a899-4149-8468-525d9a7f909d ..."
        echo "#########################################################################"
        exit 1
    else
        echo "The scripts go on............."
   fi
}

get_serveruser()
{
serverlist=$*
for i in serverlist
do
    vm_project_user=$(openstack server show -f value -c project_id -c user_id $i|paste -d "," -s)
    if [ -z $vm_project_user ]
    then
        echo "$i: server not exists."
        echo $i,null,null|tee -a export-serverlist-${TIMESTAMP}.csv
    else
        project_id=$(echo $vm_project_user|awk -F',' '{print$1}')
        user_id=$(echo $vm_project_user|awk -F',' '{print$2}')

        project_name=$(openstack project show -f value -c name $project_id)
        user_name=$(openstack user show -f value -c name $user_id)

        echo $i,$project_name,$user_name|tee -a export-serverlist-${TIMESTAMP}.csv
    fi
done
}

main()
{
server_uuid=$*
echo "Welcome to use this script to get the project and user that the server belongs to"
check_parameter ${server_uuid}

get_serveruser ${server_uuid}

}

main $@
