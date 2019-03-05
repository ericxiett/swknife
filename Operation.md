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