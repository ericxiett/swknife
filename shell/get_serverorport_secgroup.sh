#!/bin/bash

#get server or port in-use security groups


#check parameters
check_parameter()
{
	
	if [ $# -lt 2 ] 
    then 
        echo -e "Warning:The script must have two parameters."
        echo "#########################################################################"
        echo "Usage: sh $0 project_name/project_id security_id" 
        echo  -e "Example: sh $0 admin 1bd12ba4-c49d-4cac-b4a8-b3d512c46e9f"
        echo "or"
        echo  -e "Example: sh $0 4e7f9c1d7d2c4122940c0fe7e895677c 1bd12ba4-c49d-4cac-b4a8-b3d512c46e9f"
        echo "#########################################################################"
        exit 1
    else
        echo "Get server or port security group info............."    
   fi  
}

#OpenStack rc file
openrc()
{
    export OS_IDENTITY_API_VERSION=3
    export OS_AUTH_URL=http://192.168.2.10:35357/v3
    export OS_PROJECT_DOMAIN_NAME=Default
    export OS_USER_DOMAIN_NAME=Default
    export OS_PROJECT_NAME=niusdtest
    export OS_TENANT_NAME=niusdtest
    export OS_USERNAME=ebs
    export OS_PASSWORD=123456a?
    export OS_REGION_NAME=RegionOne
    export OS_INTERFACE=internal
    export OS_ENDPOINT_TYPE="internal"
    export OS_CACERT="/etc/ssl/certs/ca-certificates.crt"
    export IRONIC_API_VERSION=1.31

}

get_server_sec()
{
  
 project_info=$1
 security_id=$2

 echo "Get server using security groups:"
 openrc

 security_name=$(openstack security group list --project ${project_info} -c ID -c Name -f value|grep ${security_id}|awk -F' ' '{print$2}')

 for vm in $(openstack server list --project ${project_info} -c ID -f value);
   do

    result=$(openstack server show ${vm} -c id -c name -c security_groups -f shell|paste -d "," -s|grep ${security_name})
    if [[ ! -z ${result} ]];
    	then
    	  echo "The vm in-use security group<id=server_uuid>:${result}"
    	   
    fi	


   done

}


get_port_sec()
{

 project_info=$1
 security_id=$2
 echo "Get port using security groups:"
 openrc
 for portid in $(openstack port list --project ${project_info} -c ID -f value);
   do

   result=$(openstack port show ${portid} -c security_group_ids -c id -f shell|paste -d "," -s|grep ${security_id})
   if [[ ! -z ${result} ]];
    	then
    	   echo "The port in-use security group<id=port_id>:${result}"
    	   
    fi	
  done
}


main()
{

project_info=$1
security_id=$2

check_parameter ${project_info} ${security_id} 
echo ""
#get server security group info
get_server_sec ${project_info} ${security_id} 

echo ""
echo ""
#get port security group info
get_port_sec ${project_info} ${security_id}

}

main $@