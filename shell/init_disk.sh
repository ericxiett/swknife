#!/bin/bash
pvcreate /dev/sda /dev/sdb
vgcreate vg-k8svm /dev/sda /dev/sdb
lvcreate -L 1T -n lv-k8svm vg-k8svm
mkfs.ext4 /dev/mapper/vg--k8svm-lv--k8svm
echo "/dev/mapper/vg--k8svm-lv--k8svm /var/lib/libvirt/images ext4 defaults 0 0" >>/etc/fstab
mount -a