#!/bin/bash

function upload()
{
    url="$1"
    name="$2"
    builder="$3"
    build_at="$4"
    update_content="$5"
    os_type="$6"
    os_distro="$7"
    os_ver="$8"
    enable_qga="$9"
    wget $url -O image.qcow2
    qemu-img convert -O raw image.qcow2 image.raw
    . /root/keystonercv3
    openstack image create --file image.raw --disk-format raw --container-format bare --public --property hw_qemu_guest_agent=$enable_qga --property os_type=$os_type --property builder=$builder --property os_distro=$os_distro --property os_version=$os_ver --property build_at=$build_at $name
    rm -rf image.*
}

upload "http://10.3.32.42/images/centos65/centos65x86_64_20190104_7.qcow2" "ecs-centos6.5-x64-20190104" "aibuild" "20190104" "support 2 nics" "linux" "centos" "6.5" "yes"
upload "http://10.3.32.42/images/centos68/centos68x86_64_20190104_3.qcow2" "ecs-centos6.8-x64-20190104" "aibuild" "20190104" "support 2 nics" "linux" "centos" "6.8" "yes"
upload "http://10.3.32.42/images/centos69/centos69x86_64_20190104_2.qcow2" "ecs-centos6.9-x64-20190104" "aibuild" "20190104" "support 2 nics" "linux" "centos" "6.9" "yes"
upload "http://10.3.32.42/images/centos71/centos71x86_64_20181226_5.qcow2" "ecs-centos7.1-x64-20181226" "aibuild" "20181226" "support 2 nics" "linux" "centos" "7.1" "yes"
upload "http://10.3.32.42/images/centos73/centos73x86_64_20181224_1.qcow2" "ecs-centos7.3-x64-20181226" "aibuild" "20181226" "support 2 nics" "linux" "centos" "7.3" "yes"
upload "http://10.3.32.42/images/centos74/centos74x86_64_20181224_1.qcow2" "ecs-centos7.4-x64-20181226" "aibuild" "20181226" "support 2 nics" "linux" "centos" "7.4" "yes"
upload "http://10.3.32.42/images/WIN2008R2ENT/WIN2008R2ENTx86_64_20181226_5.qcow2" "ecs-windows2008r2_ent-x64-20181226" "aibuild" "20181226" "support qga" "windows" "2k8R2" "2k8R2ENT" "yes"
upload "http://10.3.32.42/images/WIN2008R2STD/WIN2008R2STDx86_64_20181226_22.qcow2" "ecs-windows2008r2_std-x64-20181226" "aibuild" "20181226" "support qga" "windows" "2k8R2" "2k8R2STD" "yes"
upload "http://10.3.32.42/images/WIN2012R2DC/WIN2012R2DCx86_64_20181226_11.qcow2" "ecs-windows2012r2_dc-x64-20181226" "aibuild" "20181226" "support qga" "windows" "2k12R2" "2k12R2DC" "yes"
upload "http://10.3.32.42/images/WIN2016DC/WIN2016DCx86_64_20181226_9.qcow2" "ecs-windows2016_dc-x64-20181226" "aibuild" "20181226" "support qga" "windows" "2k16" "2k16DC" "yes"
upload "http://10.3.32.42/images/ubuntu1404/ubuntu1404x86_64_20190104_5.qcow2" "ecs-ubuntu1404-x64-20190104" "aibuild" "20190104" "support 2 nics" "linux" "ubuntu" "14.04" "yes"
upload "http://10.3.32.42/images/ubuntu1604/ubuntu1604x86_64_20181220_3.qcow2" "ecs-ubuntu1604-x64-20181220" "aibuild" "20181220" "support qga" "linux" "ubuntu" "16.04" "yes"