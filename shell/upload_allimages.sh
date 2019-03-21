#!/bin/bash
function upload()
{
    tag="$1"
    #url="$1"
    name="$2"
    builder="$3"
    build_at="$4"
    update_content="$5"
    os_type="$6"
    os_distro="$7"
    os_ver="$8"
    enable_qga="$9"
    filename=${10}
    #wget $url -O image.qcow2
    qemu-img convert -O raw $filename image.raw
    . /root/keystonercv3
    openstack image create --file image.raw --disk-format raw --tag "$tag" --container-format bare --public --property hw_qemu_guest_agent=$enable_qga --property os_type=$os_type --property builder=$builder --property os_distro=$os_distro --property os_version=$os_ver --property build_at=$build_at $name
    rm -rf image.*
}
#ecs linux
upload "CentOS 7.1 64bit" "ecs-centos7.3-x64-20181226" "aibuild" "20181226" "support 2 nics" "linux" "centos" "7.3" "yes" "centos73x86_64_20181224_1.qcow2"
upload "CentOS 6.5 64bit" "ecs-centos6.5-x64-20190104" "aibuild" "20190104" "support 2 nics" "linux" "centos" "6.5" "yes" "centos65/centos65x86_64_20190104_7.qcow2"
upload "CentOS 6.8 64bit" "ecs-centos6.8-x64-20190104" "aibuild" "20190104" "support 2 nics" "linux" "centos" "6.8" "yes" "centos68/centos68x86_64_20190104_3.qcow2"
upload "CentOS 6.9 64bit" "ecs-centos6.9-x64-20190104" "aibuild" "20190104" "support 2 nics" "linux" "centos" "6.9" "yes" "centos69/centos69x86_64_20190104_2.qcow2"
upload "CentOS 7.1 64bit" "ecs-centos7.1-x64-20181226" "aibuild" "20181226" "support 2 nics" "linux" "centos" "7.1" "yes" "centos71/centos71x86_64_20181226_5.qcow2"
upload "CentOS 7.4 64bit" "ecs-centos7.4-x64-20181226" "aibuild" "20181226" "support 2 nics" "linux" "centos" "7.4" "yes" "centos74/centos74x86_64_20181224_1.qcow2"
upload "Ubuntu 14.04 64bit" "ecs-ubuntu1404-x64-20190104" "aibuild" "20190104" "support 2 nics" "linux" "ubuntu" "14.04" "yes" "ubuntu1404/ubuntu1404x86_64_20190104_5.qcow2"
upload "Ubuntu 16.04 64bit" "ecs-ubuntu1604-x64-20181220" "aibuild" "20181220" "support qga" "linux" "ubuntu" "16.04" "yes" "ubuntu1604/ubuntu1604x86_64_20181220_3.qcow2"
#ecs windows
upload "Windows Server 2008 R2 ENT 64bit" "ecs-windows2008r2_ent-x64-20181226" "aibuild" "20181226" "support qga" "windows" "2k8R2" "2k8R2ENT" "yes" "WIN2008R2ENT/WIN2008R2ENTx86_64_20181226_5.qcow2"
upload "Windows Server 2008 STD 64bit" "ecs-windows2008r2_std-x64-20181226" "aibuild" "20181226" "support qga" "windows" "2k8R2" "2k8R2STD" "yes" "WIN2008R2STD/WIN2008R2STDx86_64_20181226_22.qcow2"
upload "Windows Server 2012 R2 DC 64bit" "ecs-windows2012r2_dc-x64-20181226" "aibuild" "20181226" "support qga" "windows" "2k12R2" "2k12R2DC" "yes" "WIN2012R2DC/WIN2012R2DCx86_64_20181226_11.qcow2"
upload "Windows Server 2016 R2 DC 64bit" "ecs-windows2016_dc-x64-20181226" "aibuild" "20181226" "support qga" "windows" "2k16" "2k16DC" "yes" "WIN2016DC/WIN2016DCx86_64_20181226_9.qcow2"
#production
upload "Ubuntu 16.04 64bit" "cks-k8s-1.12.1-ubuntu16.04-2nics-20181203" "aibuild" "20181203" "support 2 nics" "linux" "ubuntu" "16.04" "no" "cks/k8s-1.12.1-ubuntu16.04-2nics.qcow2"
upload "Ubuntu 16.04 64bit" "cks-k8s-1.12.1-ubuntu16.04-20181203" "aibuild" "20181203" "support 1 nics" "linux" "ubuntu" "16.04" "no" "cks/k8s-1.12.1-ubuntu16.04.qcow2"
upload "CentOS 7.5 64bit" "hdinsight-insight4.0.1-centos7.5-x64-20190110 " "aibuild" "20190110" "support 2 nics" "linux" "centos" "7.5" "no" "hdinsight/hdinsight-insight4.0.1-centos7.5-x64_2019-03-06.qcow2"
upload "Ubuntu 14.04 64bit" "rds-mysql5.6-ubuntu14.04-x64-20190223" "aibuild" "20190223" "support 2 nics" "linux" "ubuntu" "14.04" "no" "rds-mysql5.6-ubuntu14.04-x64-20190223_2019-03-06.qcow2"
upload "CentOS 6.5 64bit" "slb-centos6.5-x64-layerall-20190127" "aibuild" "20190127" "support 2 nics" "linux" "centos" "6.5" "no" "slb-centos6.5-x64-layerall-20190127_2019-03-06.qcow2"