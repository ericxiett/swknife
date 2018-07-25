#!/bin/bash
#check openstack version

#ocata
o_nova="2:15."
o_neutron="2:10."
o_cinder="2:10."
o_glance="2:14."
o_keystone="2:11."

#pike
p_nova="2:16."
p_neutron="2:11."
p_cinder="2:11."
p_glance="2:15."
p_keystone="2:12."

#check openstack Component version
echo "">/tmp/check_version.log
for i in nova neutron cinder glance keystone;do

if [ $(dpkg -l|grep ${i}|grep $(eval echo "$"o_$i)|wc -l) -gt 0  ];then
  echo ${i} version is $(eval echo "$"o_$i) OpenStack Version:Ocata|tee -a /tmp/check_version.log
elif [ $(dpkg -l|grep ${i}|grep $(eval echo "$"p_${i})|wc -l) -gt 0  ];then
  echo ${i} version is $(eval echo "$"p_$i) OpenStack Version:Pike|tee -a /tmp/check_version.log
fi
done