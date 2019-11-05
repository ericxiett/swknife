#!/bin/bash

sethostname=$1
hostnamectl set-hostname ${sethostname}

ipnum=$(ip a|grep '10.71.'|awk '{print$2}'|cut -d'.' -f4|cut -d'/' -f1)

cat >/etc/netplan/01-netcfg.yaml<<EOF
# This file describes the network interfaces available on your system
# For more information, see netplan(5).
network:
  version: 2
  renderer: networkd
  ethernets:
    enp1s0:
      dhcp4: no
      addresses:
        - 10.71.204.${ipnum}/22
      gateway4: 10.71.207.254
    enp3s0:
      dhcp4: no
      addresses:
        - 10.71.208.${ipnum}/22
    enp6s0:
      dhcp4: no
      addresses:
        - 10.71.216.${ipnum}/22
    enp7s0:
      dhcp4: no
      addresses:
        - 10.71.212.${ipnum}/22                      
EOF

netplan apply