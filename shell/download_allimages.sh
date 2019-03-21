#!/bin/bash

function download()
{
    echo "Starting to download $1 $2..."
    OSINFO="$1"
    IMAGE="$2"
    mkdir -p /opt/images/${OSINFO}/
    cd /opt/images/${OSINFO}/
    wget -q -c http://117.73.1.11/images/${OSINFO}/${IMAGE}
    md5sum ${IMAGE} >> md5sum.txt
    echo "Finish to download $1 $2!"
}

# ecs
download centos71 centos71x86_64_20181226_5.qcow2
download centos69 centos69x86_64_20190104_2.qcow2
download centos68 centos68x86_64_20190104_3.qcow2
download centos65 centos65x86_64_20190104_7.qcow2
download centos74 centos74x86_64_20181224_1.qcow2
download centos73 centos73x86_64_20181224_1.qcow2
download ubuntu1404 ubuntu1404x86_64_20190104_5.qcow2
download ubuntu1604 ubuntu1604x86_64_20181220_3.qcow2

download WIN2016DC WIN2016DCx86_64_20181226_9.qcow2
download WIN2012R2DC WIN2012R2DCx86_64_20181226_11.qcow2
download WIN2008R2STD WIN2008R2STDx86_64_20181226_22.qcow2
download WIN2008R2ENT WIN2008R2ENTx86_64_20181226_5.qcow2


# product
download cks k8s-1.12.1-ubuntu16.04-2nics.qcow2
download cks k8s-1.12.1-ubuntu16.04.qcow2
download hdinsight hdinsight-insight4.0.1-centos7.5-x64_2019-03-06.qcow2