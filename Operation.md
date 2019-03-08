# OpenStack平台数据初始化
此操作说明文档描述在openstack平台初始化设置或脚本执行的操作说明。

## 1 配额修改
修改默认配额为-1无限制
脚本位置swknife/shell/set_default_quotas.sh
```shell
salt-cp 'ctl*' set_default_quotas.sh /usr/local/src/
salt 'ctl*' cmd.run 'chmod +x /usr/local/src/set_default_quotas.sh;\
bash /usr/local/src/set_default_quotas.sh>>/var/log/quotas.log' --async
```
执行完毕后在任一ctl节点，创建项目验证
```shell
source /root/keystonercv3
openstack project show test_quotas_project
openstack quota show test_quotas_project
```
## 2 创建管理用户
* 构建python执行环境
```shell
#安装虚拟环境
apt install virtualenv -y
#创建虚拟环境
cd /usr/local/src
virtualenv pysrc
#进入虚拟环境
source pysrc/bin/activate
#安装依赖基础包
apt install gcc gcc+ make python-dev -y
#安装openstackclient
pip install python-openstackclient
#安装工具软件
pip install xlwt xlrd
```
* python脚本使用执行
```
cd /usr/local/src
git clone https://github.com/ericxiett/swknife.git
cd swknife
```
修改脚本create_adminuser.py认证信息
```python
AUTH_URL='http://192.168.2.10:35357/v3'
USERNAME = 'admin'
PASSWORD = '123456333'
PROJECT_NAME = 'admin'
DOMAIN_NAME = 'Default'
DOMAIN_ID = 'default'
REGION_NAME = 'RegionOne'
```
脚本执行
```
python create_adminuser.py
```
执行完毕会输出结果文件：Inspurcloud-poss_users.xls

## 3划分资源池（创建主机聚合）
进入swknife/python目录,修改create_host_aggregate.py里认证信息，然后执行
```shell
python create_host_aggregate.py staging_swknife_collect.xlsx
```
部分输出信息：
```
Operation is Finish.
----------------------------
HgName: cn-sourth-1a_slb_lvs_general
Status: SUCCESS
----------------------------
HgName: cn-sourth-1a_slb_nginx_general
Status: SUCCESS
----------------------------
HgName: cn-sourth-1a_cks_general
Status: SUCCESS
----------------------------
HgName: cn-sourth-1a_ecs_general
Status: SUCCESS
----------------------------
HgName: cn-sourth-1a_hdinsight_general
Status: SUCCESS
----------------------------
HgName: cn-sourth-1a_reserve_general
Status: SUCCESS

```
在控制节点验证主机聚合创建结果
```shell
root@ctl01:~# openstack aggregate list
+----+--------------------------------+-------------------+
| ID | Name                           | Availability Zone |
+----+--------------------------------+-------------------+
|  3 | cn-sourth-1a_slb_lvs_general   | cn-sourth-1a      |
|  6 | cn-sourth-1a_slb_nginx_general | cn-sourth-1a      |
|  9 | cn-sourth-1a_cks_general       | cn-sourth-1a      |
| 12 | cn-sourth-1a_ecs_general       | cn-sourth-1a      |
| 15 | cn-sourth-1a_hdinsight_general | cn-sourth-1a      |
| 18 | cn-sourth-1a_reserve_general   | cn-sourth-1a      |
+----+--------------------------------+-------------------+
root@ctl01:~# openstack aggregate show cn-sourth-1a_slb_lvs_general
+-------------------+-----------------------------------+
| Field             | Value                             |
+-------------------+-----------------------------------+
| availability_zone | cn-sourth-1a                      |
| created_at        | 2019-03-05T01:41:38.000000        |
| deleted           | False                             |
| deleted_at        | None                              |
| hosts             | [u'cmp001', u'cmp002']            |
| id                | 3                                 |
| name              | cn-sourth-1a_slb_lvs_general      |
| properties        | SERVICE='SLB_LVS', SPEC='GENERAL' |
| updated_at        | None                              |
+-------------------+-----------------------------------+

```
## 4创建flavor
执行过程
```shell
cd swknife/python
#加载认证环境变量信息，没有须根据环境信息创建
source keystonercv3
(pysrc)/usr/local/src/swknife/python# python create_required_flavors.py -f staging_swknife_collect.xlsx  -i 1
[[2019-03-05 10:06:14,118] - INFO - __main__.269 - create flavor ecs_32C128G450G_general
[2019-03-05 10:06:14,177] - INFO - __main__.269 - create flavor ecs_32C128G460G_general
[2019-03-05 10:06:14,241] - INFO - __main__.269 - create flavor ecs_32C128G470G_general
[2019-03-05 10:06:14,305] - INFO - __main__.269 - create flavor ecs_32C128G480G_general
[2019-03-05 10:06:14,371] - INFO - __main__.269 - create flavor ecs_32C128G490G_general
[2019-03-05 10:06:14,433] - INFO - __main__.269 - create flavor ecs_32C128G500G_general
[2019-03-05 10:06:14,499] - INFO - root.382 - finishes creating flavors
#在控制节点验证创建的flavor信息
root@ctl01:~# openstack flavor show dec448bc-e17d-463c-9089-348191397fdd
+----------------------------+----------------------------------------------------------------------------------------------------------+
| Field                      | Value                                                                                                    |
+----------------------------+----------------------------------------------------------------------------------------------------------+
| OS-FLV-DISABLED:disabled   | False                                                                                                    |
| OS-FLV-EXT-DATA:ephemeral  | 0                                                                                                        |
| access_project_ids         | None                                                                                                     |
| disk                       | 250                                                                                                      |
| id                         | dec448bc-e17d-463c-9089-348191397fdd                                                                     |
| name                       | ecs_4C8G250G_general                                                                                     |
| os-flavor-access:is_public | True                                                                                                     |
| properties                 | SERVICE='ECS', SPEC='GENERAL', quota:vif_inbound_average='1048576', quota:vif_outbound_average='1048576' |
| ram                        | 8192                                                                                                     |
| rxtx_factor                | 1.0                                                                                                      |
| swap                       |                                                                                                          |
| vcpus                      | 4                                                                                                        |
+----------------------------+----------------------------------------------------------------------------------------------------------+

```
## 5创建服务产品管理网
程序使用
```python
(pysrc) root@bmk01:/usr/local/src/swknife/python# python created_requested_network.py 
usage: created_requested_network.py [-h] -f CONFIG_PATH [-d] [-o OUTPUT_FILE]
                                    [-i INDEX]

```
程序执行
```python
python created_requested_network.py -f staging_swknife_collect.xlsx -o mgmnetwork_create20190305.xlsx -i 3
```
output
```
INFO:__main__:create network <__main__.Network object at 0x7fe248185e90>
INFO:__main__:network id: 01cc078e-2fc6-48a3-ba53-4de7608df4f4
INFO:root:subnets obtained []
INFO:__main__:successfully create network:subnet slb_mgmt:slb_subnet
INFO:__main__:create network <__main__.Network object at 0x7fe24652d250>
INFO:__main__:network id: e7e1aa4c-d21d-4f1b-a589-d2e06861968b
INFO:root:subnets obtained []
INFO:__main__:successfully create network:subnet slb_data:slb_subnet
INFO:__main__:create network <__main__.Network object at 0x7fe24652d350>
INFO:__main__:network id: c140e573-a614-4b68-81ba-379bc07d07ae
INFO:root:subnets obtained []
INFO:__main__:successfully create network:subnet rds_mgmt:rds_subnet
INFO:__main__:create network <__main__.Network object at 0x7fe24652d390>
INFO:__main__:network id: 51279957-b77d-426f-ad39-1bf4a9a4bd3f
INFO:root:subnets obtained []
INFO:__main__:successfully create network:subnet hdinsight_mgmt:hdinsight_subnet
INFO:__main__:create network <__main__.Network object at 0x7fe24652d110>
INFO:__main__:network id: 1c0dc99d-4f70-4c20-a63c-4da57c9c7d4b
INFO:root:subnets obtained []
INFO:__main__:successfully create network:subnet cks_mgmt:cks_subnet
```
## 6创建卷类型
```shell
root@ctl01:~# source keystonercv3
root@ctl01:~# openstack volume type create --property volume_backend_name='ceph' SATA
+-------------+--------------------------------------+
| Field       | Value                                |
+-------------+--------------------------------------+
| description | None                                 |
| id          | 2de857bd-3594-4bc2-a8dc-105b3d17afb0 |
| is_public   | True                                 |
| name        | SATA                                 |
| properties  | volume_backend_name='ceph'           |
+-------------+--------------------------------------+

```
## 7镜像上传
* 镜像下载  
  通过url下载，脚本：download_allimages.sh
```shell
download centos71 centos71x86_64_20181226_5.qcow2
download centos69 centos69x86_64_20190104_2.qcow2
download centos68 centos68x86_64_20190104_3.qcow2
download centos65 centos65x86_64_20190104_7.qcow2
download centos74 centos74x86_64_20181224_1.qcow2
download centos73 centos73x86_64_20181224_1.qcow2
download WIN2016DC WIN2016DCx86_64_20181226_9.qcow2
download WIN2012R2DC WIN2012R2DCx86_64_20181226_11.qcow2
download WIN2008R2STD WIN2008R2STDx86_64_20181226_22.qcow2
download WIN2008R2ENT WIN2008R2ENTx86_64_20181226_5.qcow2
download ubuntu1404 ubuntu1404x86_64_20190104_5.qcow2
download ubuntu1604 ubuntu1604x86_64_20181220_3.qcow2
download cks k8s-1.12.1-ubuntu16.04-2nics.qcow2
download cks k8s-1.12.1-ubuntu16.04.qcow2
download hdinsight hdinsight-insight4.0.1-centos7.5-x64_2019-03-06.qcow2
```

* 镜像上传  
  通过命令行上传方式：  
  ```shell
  source /root/keystonercv3
  #Pay attention to the variable $var
  openstack image create --file image.raw --disk-format raw --tag "$tag" --container-format bare --public --property hw_qemu_guest_agent=$enable_qga --property os_type=$os_type --property builder=$builder --property os_distro=$os_distro --property os_version=$os_ver --property build_at=$build_at $name

   ```
   通过脚本方式：根据实际环境进行修改    
   脚本：upload_allimages.sh  
   ```shell
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

   ```
 * 查看验证
   ```shell
   root@ctl01:/tmp# openstack image list --long  -c ID -c Name -c Tags
   +--------------------------------------+-----------------------------------------------+---------------------------------+
   | ID                                   | Name                                          | Tags                            |
   +--------------------------------------+-----------------------------------------------+---------------------------------+
   | aac11960-63bf-4a45-b6bb-cd8ebe77f946 | Ubuntu                                        |                                 |
   | 1c8b123b-d591-4696-a6a0-a73daba82045 | centos72x86_64.qcow2                          |                                 |
   | 528436ad-b163-411c-bfd0-c3fc0d85c964 | cks-k8s-1.12.1-ubuntu16.04-20181203           | Ubuntu 16.04 64bit              |
   | 1a1613c4-e706-47ec-bcec-8e14f78b9969 | cks-k8s-1.12.1-ubuntu16.04-2nics-20181203     | Ubuntu 16.04 64bit              |
   | 04015b5e-445f-4f10-a3d3-93e4f4239ce8 | ecs-centos6.5-x64-20190104                    | CentOS 6.5 64bit                |
   | b1ef5211-a57a-4c48-9d87-1ccff6baa594 | ecs-centos6.8-x64-20190104                    | CentOS 6.8 64bit                |
   | 6107e23f-fb55-4508-8773-bc3721114dc4 | ecs-centos6.9-x64-20190104                    | CentOS 6.9 64bit                |
   | 01f8797b-5ea4-4ad4-a9dc-f5f11c24ee4d | ecs-centos7.1-x64-20181226                    | CentOS 7.1 64bit                |
   | 32253b86-6177-4b62-a8e6-b9b10fc94a0d | ecs-centos7.3-x64-20181226                    | CentOS 7.3 64bit                |
   | be583825-1d9d-40ad-a425-1b3994925137 | ecs-centos7.4-x64-20181226                    | CentOS 7.4 64bit                |
   | 381a0240-5fc2-4343-bb90-07d16d11f4ee | ecs-ubuntu1404-x64-20190104                   | Ubuntu 14.04 64bit              |
   | baf240a6-3c3b-4781-9ba4-d77a5d076c25 | ecs-ubuntu1604-x64-20181220                   | Ubuntu 16.04 64bit              |
   | 8aa6c45e-e8fd-41e8-8e7a-407c11a40aea | ecs-windows2012r2_dc-x64-20181226             | Windows Server 2012 R2 DC 64bit |
   | 6343ba12-3674-4456-b3a9-dfe4deb87c1e | ecs-windows2016_dc-x64-20181226               | Windows Server 2016 R2 DC 64bit |
   | 85a27e0f-3acc-477c-87ab-5cbd5eb892f8 | hdinsight-insight4.0.1-centos7.5-x64-20190110 | CentOS 7.5 64bit                |
   | a00830cc-acab-4dc0-915d-5717e6109383 | image                                         |                                 |
   | 4139dd9b-b418-4d9c-bc3a-3784a8ebc197 | rds-mysql5.6-ubuntu14.04-x64-20190223         | Ubuntu 14.04 64bit              |
   | 89b5296b-64b1-48b3-be70-302367a749c7 | slb-centos6.5-x64-layerall-20190127           | CentOS 6.5 64bit                |
   | 05c5b69c-1c2c-46ca-9a16-30f084d8c39a | test-image                                    |                                 |
   | c4490eed-8235-4fe0-be0a-558622c55198 | test-image                                    |                                 |
   | a923e29b-00c4-46c7-9e77-61fd66b53adb | testvm                                        |                                 |
   +--------------------------------------+-----------------------------------------------+---------------------------------+
   #注意hw_qemu_guest_agent参数设置
   root@ctl01:/tmp# for i in $(openstack image list -f value -c ID);do openstack image show $i -f value -c id -c name -c properties -c tags|paste -d' ' -s;echo "##";done
   528436ad-b163-411c-bfd0-c3fc0d85c964 cks-k8s-1.12.1-ubuntu16.04-20181203 build_at='20181203', builder='aibuild', direct_url='rbd://5fde40dc-b512-c2a5-27d1-f7d8da3cee51/images/528436ad-b163-411c-bfd0-c3fc0d85c964/snap', hw_qemu_guest_agent='no', os_distro='ubuntu', os_type='linux', os_version='16.04' Ubuntu 16.04 64bit
   ##
   04015b5e-445f-4f10-a3d3-93e4f4239ce8 ecs-centos6.5-x64-20190104 build_at='20190104', builder='aibuild', direct_url='rbd://5fde40dc-b512-c2a5-27d1-f7d8da3cee51/images/04015b5e-445f-4f10-a3d3-93e4f4239ce8/snap', hw_qemu_guest_agent='yes', os_distro='centos', os_type='linux', os_version='6.5' CentOS 6.5 64bit
   ```