#!/usr/bin/env python
# _*_ coding:utf-8 _*_
#
# __author__ = "song.w"


from random import choice
import string
import xlwt
from keystoneauth1 import loading, session
from keystoneclient.v3 import client

AUTH_URL='http://192.168.2.10:35357/v3'
USERNAME = 'admin'
PASSWORD = '89rqdHLMN5rm0x1P'
PROJECT_NAME = 'admin'
DOMAIN_NAME = 'Default'
DOMAIN_ID = 'default'
P_PROJECT="poss"
USERLIST=["ecs_admin","slb_admin"]

FIELDS = ['index', 'user_name', 'user_password', 'project_name','project_id']

#VALID_USERS = ['ecs_admin', 'slb_admin','ebs_admin','cks_admin']

def build_sheet():
    style0 = xlwt.easyxf('font: name Times New Roman, color-index green, bold on',
                         num_format_str='#,##0')
    style1 = xlwt.easyxf('font: name Times New Roman, color-index black',
                         num_format_str='#,##0')

    wb = xlwt.Workbook()
    ws = wb.add_sheet('users')

    # First row
    for col in range(len(FIELDS)):
        ws.write(0, col, FIELDS[col], style0)

    return wb, ws, style1

def output_users(wb, ws, style,index,username, password,project_name,project_id):

    #wb, ws, style = build_sheet()

    ws.write(index, 0, index, style)
    ws.write(index, 1, username, style)
    ws.write(index, 2, password, style)
    ws.write(index, 3, project_name, style)
    ws.write(index, 4, project_id, style)

    wb.save('boss_users.xls')

def get_keystone_client():
    loader = loading.get_plugin_loader('password')
    auth = loader.load_from_options(auth_url=AUTH_URL,
                                    username=USERNAME,
                                    password=PASSWORD,
                                    project_name=PROJECT_NAME,
                                    user_domain_name=DOMAIN_NAME,
                                    project_domain_name=DOMAIN_NAME)
    sess = session.Session(auth=auth)
    return client.Client(session=sess)

def Makepass(length=15, chars=string.letters+string.digits):
    #password create
    return ''.join([choice(chars) for i in range(length)])

def get_keystone_projects():
    #obtain all projects
    keystone = get_keystone_client()
    project_list=keystone.projects.list()
    return project_list

def create_project(project_name,domain_id):
    keystone = get_keystone_client()
    flag = 0
    for project in get_keystone_projects():
        if project_name == project.name:
            print("Project:%s already exists."% project_name)
            flag = 1
            break

    if flag == 0:
        project=keystone.projects.create(project_name,domain_id,description=None,
               enabled=True)
        print("Project:%s create successful." % project_name)
    return project.id

def create_user(u_name, domain, project, password,
               email=None, description=None, enabled=True):
    keystone = get_keystone_client()
    user_name = keystone.users.list(name=u_name)
    user_flag = 0
    for user in user_name:
        if user.name == u_name:
            print("User:%s already exists" %user.id)
            user_flag = 1

    if user_flag == 0:
        try:
            user = keystone.users.create(u_name, domain, project, password,
                   email=None, description=None, enabled=True)
            print("user:%s ,passwd: %s create successful" % (user.name,password))

        except Exception:
            print("user:%s  create failure" % (u_name))
    return user.id,user_flag

def user_grant(role_id,user_id,project_id):

    keystone = get_keystone_client()
    keystone.roles.grant(role_id,user=user_id,project=project_id)
    print("user:%s grant role:%s successful" % (user_id, role_id))

def get_admin_role():
    keystone = get_keystone_client()
    for  admin_role in keystone.roles.list(name="admin"):
        role_id = admin_role.id
    return  role_id


def main():
    print('Welcome to use this script,create project and user')
    project_name = P_PROJECT
    domain_id = DOMAIN_ID

    project_id = create_project(project_name, domain_id)
    print("project_id:%s" % project_id)
    #init xlsx
    wb, ws, style = build_sheet()
    index = 1
    for username in USERLIST:
        userpass = Makepass()
        userid,u_flag = create_user(username, domain=domain_id, project=project_id, password=userpass,
              email=None, description=None, enabled=True)
        print("user_id:%s" %userid )
        if u_flag == 1:
            userpass=""

        role_id = get_admin_role()
        print("role_id:%s" %role_id )
        user_grant(role_id, userid, project_id)
        #if user exist password ""
        output_users(wb, ws, style,index, username, userpass, project_name, project_id)
        index +=1
    return 0

if __name__ == '__main__':

    exit(main())