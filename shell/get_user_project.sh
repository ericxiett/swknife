#!/bin/bash
# $* mutil parameters

check_parameter()
{

	if [ $# -lt 1 ]
    then
        echo -e "Warning:The script must have one parameters."
        echo "#########################################################################"
        echo "Usage: sh $0 username"

        echo  -e "Example: sh $0 a6c6a683-5419-4ed8-8bfb-69e2c24f269f"
        echo "or"
        echo  -e "Example: sh $0 a6c6a683-5419-4ed8-8bfb-69e2c24f269f 15794036-a899-4149-8468-525d9a7f909d ..."
        echo "#########################################################################"
        exit 1
    else
        echo "The scripts go on............."
   fi
}

get_userproject()
{
userlist=$*
for i in $userlist
  do
  userid=$(openstack user list -f value -c ID -c Name|grep $i|awk -F' ' '{print$1}')
  if [ -z $userid ]
  then
     echo "user : $i,not found"
  else
     projectid=$(openstack  role assignment list --user $userid -f value -c Project)
     projectname=$(openstack project show ${projectid} -f value -c name)

     echo "user name:${i},own project_name:${projectname},project_id:${projectid}"
   fi
done
}

main()
{
user_name=$*
echo "Welcome to use this script to get the project that the user belongs to"
check_parameter ${user_name}

get_userproject ${user_name}

}

main $@

#single line cli
#userid="87c0031b-376c-4f92-a0f6-c70180de1781"
#openstack project show $(openstack  role assignment list --user $(openstack user \
#list -f value -c ID -c Name|grep ${userid}|awk -F' ' '{print$1}') -f value -c Project) -f value -c name