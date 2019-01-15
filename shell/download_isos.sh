#!/usr/bin/env bash

set -e

BASEDIR="/var/www/html/isos"
# CentOS
cd $BASEDIR/centos
centos_array=(
"https://mirrors.tuna.tsinghua.edu.cn/centos-vault/6.5/isos/x86_64/CentOS-6.5-x86_64-minimal.iso"
"https://mirrors.tuna.tsinghua.edu.cn/centos-vault/6.8/isos/x86_64/CentOS-6.8-x86_64-minimal.iso"
"https://mirrors.tuna.tsinghua.edu.cn/centos-vault/6.9/isos/x86_64/CentOS-6.9-x86_64-minimal.iso"
"https://mirrors.tuna.tsinghua.edu.cn/centos-vault/7.1.1503/isos/x86_64/CentOS-7-x86_64-Minimal-1503-01.iso"
"https://mirrors.tuna.tsinghua.edu.cn/centos-vault/7.2.1511/isos/x86_64/CentOS-7-x86_64-Minimal-1511.iso"
"https://mirrors.tuna.tsinghua.edu.cn/centos-vault/7.3.1611/isos/x86_64/CentOS-7-x86_64-Minimal-1611.iso"
"https://mirrors.tuna.tsinghua.edu.cn/centos-vault/7.4.1708/isos/x86_64/CentOS-7-x86_64-Minimal-1708.iso"
""
)
for ((i=0;i<${#centos_array[*]};i++))
do
wget ${centos_array[$i]}
done
