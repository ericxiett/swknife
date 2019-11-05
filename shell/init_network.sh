#!/bin/bash
cp /etc/network/interfaces /opt/vms/interfaces_bak_$(date "+%Y-%m-%d-%H-%M-%S")

cat >/etc/network/interfaces <<EOF
# This file describes the network interfaces available on your system
# and how to activate them. For more information, see interfaces(5).

source /etc/network/interfaces.d/*

# The loopback network interface
auto lo
iface lo inet loopback

auto enp17s0f0
iface enp17s0f0 inet manual
    bond-master bond0

auto enp17s0f1
iface enp17s0f1 inet manual
    bond-master bond0

auto bond0
iface bond0 inet manual
    bond-mode active-backup
    bond-miimon 100
    bond-slaves enp17s0f0 enp17s0f1

auto br-mgt
iface br-mgt inet static
    address 10.71.204.$1
    gateway 10.71.207.254
    netmask 255.255.252.0
    bridge_ports bond0

auto enp17s0f2
iface enp17s0f2 inet manual
    bond-master bond1

auto enp17s0f3
iface enp17s0f3 inet manual
    bond-master bond1

auto bond1
iface bond1 inet  manual
    bond-mode active-backup
    bond-miimon 100
#    bond-ad_select 0
#    bond-downdelay 200
#    bond-lacp_rate 0
#    bond-miimon 100
#    bond-mode 4
#    bond-updelay 0
    bond-use_carrier off
#    bond-xmit_hash_policy layer3+4
    bond-slaves enp17s0f2 enp17s0f3

auto bond1.3208
iface bond1.3208 inet manual
    vlan-raw-device bond1
#iface bond1 inet static
#    address 10.71.208.$1
#    netmask 255.255.252.0
	
#auto enp6s0f0
#iface enp6s0f0 inet manual
#    bond-master bond2
#
#
#auto enp6s0f1
#iface enp6s0f1 inet manual
#    bond-master bond2
#
#auto bond2
#iface bond2 inet manual
#    bond-mode active-backup
#    bond-miimon 100
##    bond-ad_select 0
##    bond-downdelay 200
##    bond-lacp_rate 0
##    bond-miimon 100
##    bond-mode 4
#    bond-slaves enp6s0f0 enp6s0f1
##    bond-updelay 0
##    bond-use_carrier on
##    bond-xmit_hash_policy layer3+4
#
#auto bond2.3216
#iface bond2.3216 inet static
#    vlan-raw-device bond2
#    address 10.71.216.$1
#    netmask 255.255.252.0

auto enp6s0f1
iface enp6s0f1 inet manual
##data
auto br-sdata
iface br-sdata inet static
    address 10.71.216.$1
    netmask 255.255.252.0
    bridge_ports enp6s0f1.3216
    
auto enp6s0f1.3216
iface enp6s0f1.3216 inet manual
    vlan-raw-device enp6s0f1
##control
auto br-ctl
iface br-ctl inet static
    address 10.71.208.$1
    netmask 255.255.252.0
    bridge_ports bond1.3208
    
##storage
auto br-storpub
iface br-storpub inet static
    bridge_ports enp6s0f1.3212
    address 10.71.212.$1
    netmask 255.255.252.0
    
auto enp6s0f1.3212
iface enp6s0f1.3212 inet manual   
    vlan-raw-device enp6s0f1
EOF