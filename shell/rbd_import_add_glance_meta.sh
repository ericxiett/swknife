#!/bin/bash

set -x

if [[ -z "$1" || -z "$2" ]];then
    echo "Please input image file need to be uploaded!"
    echo "arg1: image file"
    echo "arg2: image name in glance"
    exit 1
fi

# Importing images into RBD with qemu-img convert
export IMAGE_ID=`uuidgen`
export POOL="glance.images"  # replace with your Glance pool name

imgfile="$1"
qemu-img convert -f qcow2 -O raw ${imgfile} rbd:$POOL/$IMAGE_ID

# Creating the clone baseline snapshot
rbd -p glance.images snap ls $IMAGE_ID
rbd -p glance.images snap create --snap snap $IMAGE_ID
rbd -p glance.images snap ls $IMAGE_ID

rbd -p glance.images snap protect --image $IMAGE_ID --snap snap

# Making Glance aware of the image
imgname="$2"
source /root/admin-openrc.sh
glance image-create --disk-format raw \
--container-format bare \
--visibility public \
--name ${imgname} \
--id $IMAGE_ID

glance  location-add --url rbd://$(ceph fsid)/glance.images/$IMAGE_ID/snap $IMAGE_ID 

openstack image set --property hw_firmware_type='uefi'  $IMAGE_ID

