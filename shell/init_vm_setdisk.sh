#!/bin/bash

set -x

pvcreate /dev/vda
vgcreate vg-data /dev/vda
lvcreate -L 20G -n lv-docker vg-data
lvcreate -L 20G -n lv-kubelet vg-data
lvcreate -L 18G -n lv-log vg-data

mkdir /home/back
cp -a /var/log/* /home/back/
mkfs.ext4 /dev/mapper/vg--data-lv--log 
lvlog=$(blkid|grep log|cut -d" " -f2)
echo "${lvlog} /var/log ext4 defaults 0 0" >>/etc/fstab
cp -a /home/back/* /var/log/

mkdir -p /var/lib/{docker,kubelet}
mkfs.ext4 /dev/mapper/vg--data-lv--docker 
mkfs.ext4 /dev/mapper/vg--data-lv--kubelet
lvdocker=$(blkid|grep docker|cut -d" " -f2)
lvkubelet=$(blkid|grep kubelet|cut -d" " -f2)
echo "${lvdocker} /var/lib/docker ext4 defaults 0 0" >>/etc/fstab
echo "${lvkubelet} /var/lib/kubelet ext4 defaults 0 0" >>/etc/fstab
mount -a

df -h
service docker restart