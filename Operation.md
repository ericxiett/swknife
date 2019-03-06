# Openstack平台数据初始化
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
```python
python create_host_aggregate.py staging_swknife_collect.xlsx
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