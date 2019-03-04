#!/bin/bash
set -x
DATES=$(date "+%Y-%m-%d")

# nova quotas
set_compute()
{
nova quota-class-show default

nova quota-class-update --instances -1 default
nova quota-class-update --cores -1 default
nova quota-class-update --ram -1 default 
nova quota-class-update --key-pairs -1 default
nova quota-class-update --server-groups -1 default
nova quota-class-update --server-group-members -1 default

nova quota-class-show default	
}

# cinder quotas
set_cinder()
{
cinder quota-class-show default

cinder quota-class-update --volumes -1 default
cinder quota-class-update --gigabytes -1 default
cinder quota-class-update --snapshots -1 default
cinder quota-class-update --backup-gigabytes -1 default
cinder quota-class-update --backups -1 default
cinder quota-class-show default
}


# neutron quotas ,need modify neutron.conf configuration file

#quota_network = -1
#quota_subnet = -1
#quota_port = -1
#quota_router = -1
#quota_floatingip = -1
#quota_security_group = -1
#quota_security_group_rule = -1



del_quotas()
{
sed -i '/^quota_network = -1/d' /etc/neutron/neutron.conf
sed -i '/^quota_subnet = -1/d'  /etc/neutron/neutron.conf
sed -i '/^quota_port = -1/d'  /etc/neutron/neutron.conf
sed -i '/^quota_router = -1/d' /etc/neutron/neutron.conf
sed -i '/^quota_floatingip = -1/d' /etc/neutron/neutron.conf
sed -i '/^quota_security_group = -1/d' /etc/neutron/neutron.conf
sed -i '/^quota_security_group_rule = -1/d' /etc/neutron/neutron.conf	
}

main()
{
#backup neutron.conf
cp -ar /etc/neutron/neutron.conf /etc/neutron/neutron.conf_$(date "+%Y-%m-%d")

del_quotas

sed -i '/^\[quotas\]/a quota_network = -1\nquota_subnet = -1\nquota_port = -1\nquota_router = -1\nquota_floatingip = -1\nquota_security_group = -1\nquota_security_group_rule = -1' /etc/neutron/neutron.conf

grep -E '^\[quotas\]' /etc/neutron/neutron.conf -A 7

systemctl restart neutron-server

sleep 15

if [[ $(hostname) == "ctl01" ]];
	then
    . /root/keystonercv3
    set_compute
    set_cinder
    del_quotas
else
    del_quotas
fi

}

main $@