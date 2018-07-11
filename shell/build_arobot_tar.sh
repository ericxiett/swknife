#!/bin/bash

set -ex

# Ensure required rpms installed
yum install -y git wget createrepo

# Build rpms of ironic and ironic-inspector
git clone https://github.com/ericxiett/arobot_contrib.git
base_path=$(cd `dirname $0`; pwd)
contrib_path=$base_path/arobot_contrib
cd $contrib_path
sh build_rpm.sh

# Download third depended rpms
cd $base_path
thirddeps_path=$base_path/third_deps/
if [[ -d $thirddeps_path ]]; then
    rm -rf $thirddeps_path
fi
wget http://172.23.59.135/arobot_contrib/third_deps.tar
tar -xvf third_deps.tar

# Merge rpms to one dir
deps_path=$base_path/arobot_deps
if [[ -d $deps_path ]]; then
    rm -rf $deps_path
fi
mkdir -p $deps_path
cp $thirddeps_path/* $deps_path
cp $contrib_path/rpms/ironic/* $deps_path
cp $contrib_path/rpms/ironic-inspector/* $deps_path

# Tar deps
createrepo $deps_path
tar -cvf arobot_deps.tar arobot_deps/

# Clone ansible_arobot
ansible_path=$base_path/ansible_arobot
if [[ -d $ansible_path ]]; then
    rm -rf $ansible_path
fi
git clone https://github.com/ericxiett/ansible_arobot.git

# Setup contrib
mkdir $ansible_path/contrib
cp arobot_deps.tar $ansible_path/contrib

# Build arobot.tar and copy to files/
arobot_path=$base_path/arobot
if [[ -d $arobot_path ]]; then
    rm -rf $arobot_path
fi
git clone https://github.com/ericxiett/arobot.git
tar -cvf arobot.tar arobot/
files_path=$ansible_path/files
cp arobot.tar $files_path

# Download deploy ramdisk and copy to files/
cd $files_path
wget http://172.23.59.135/deploy_ramdisk/deploy-latest.initramfs
wget http://172.23.59.135/deploy_ramdisk/deploy-latest.vmlinuz
mv deploy-latest.initramfs deploy.initramfs
mv deploy-latest.initramfs deploy.vmlinuz

cd $base_path
tar -cvf ansible_arobot.tar ansible_arobot/
