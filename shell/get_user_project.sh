#!/bin/bash

userlist="a6c6a683-5419-4ed8-8bfb-69e2c24f269f  15794036-a899-4149-8468-525d9a7f909d e53c577c-a215-45df-beaf-589fdaddfa3d"

for i in $userlist
  do

  userid=$(openstack user list -f value -c ID -c Name|grep $i|awk -F' ' '{print$1}')

  projectid=$(openstack  role assignment list --user $userid -f value -c Project)

  projectname=$(openstack project show ${projectid} -f value -c name)

  echo "user name:${i},own project_name:${projectname},project_id:${projectid}"

done