import os

from glanceclient import Client as glancec
from keystoneauth1 import loading, session
from keystoneclient.v3 import client as keystonec
from novaclient import client as novac

NOVA_VER = '2.53'


def get_nova_client():
    sess = create_session()
    return novac.Client(NOVA_VER, session=sess, endpoint_type='admin')

def get_keystone_client():
    sess = create_session()
    return keystonec.Client(session=sess, interface='admin')

def get_glance_client():
    sess = create_session()
    return glancec('2', session=sess, interface='admin')


def create_session():
    loader = loading.get_plugin_loader('password')
    auth = loader.load_from_options(
        auth_url=os.environ.get('OS_AUTH_URL'),
        username=os.environ.get('OS_USERNAME'),
        password=os.environ.get('OS_PASSWORD'),
        project_name=os.environ.get('OS_PROJECT_NAME'),
        user_domain_name=os.environ.get('OS_USER_DOMAIN_NAME'),
        project_domain_name=os.environ.get('OS_PROJECT_DOMAIN_NAME'))
    sess = session.Session(auth=auth, verify=False)
    return sess
