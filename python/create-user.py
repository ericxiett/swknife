#!/usr/bin/env python
# -*- coding: utf-8 -*-


import string
import random
import os
import logging
from keystoneauth1 import session, loading
from keystoneclient.v3 import client
from xlrd import open_workbook
import xlwt

DEFAULT_SPEC = "general"
LOGGER = None
COLUME_NAME = ["service", "name", "password", "project", "role"]
MAX_COLUMNS = len(COLUME_NAME)
DEFAULT_NIC = "physnet1"


def get_logger():
    global LOGGER
    if not LOGGER:
        LOGGER = logging.getLogger(__name__)
    return LOGGER


def setup_logging(debug=False):
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level)


class SimplePasswordGenerator(object):
    @classmethod
    def generate(cls):
        all_together = string.ascii_letters + "!@$#%^&?_-"
        result = ""
        while len(result) < 14:
            a = random.randint(0, len(all_together) - 1)
            result += all_together[a]

        return result


class User(object):
    """
    network object
    """

    def __init__(self, service, name, password, project, role="admin"):
        """
        create user
        """
        self.service = service
        self.password = password if password else SimplePasswordGenerator.generate()
        self.name = name
        self.project = project
        self.role = role
        self.logger = get_logger()

    @classmethod
    def create(cls, service, name, password, project, role="admin"):

        return User(service, name, password, project, role)

    def create_user(self, keystone_client):

        default_domain = "default"

        roles = keystone_client.roles.list()
        for role in roles:
            if role.name == self.role:
                role_obj = role
                break
        else:
            role_obj = keystone_client.roles.create(self.role, default_domain)

        if not self.project:
            self.logger.warning("user %s does not have a project assoicated", self.name)
            return

        projects = keystone_client.projects.list(domain=default_domain)
        for exist in projects:
            if exist.name == self.project:
                project_obj = exist
                break
        else:
            project_obj = keystone_client.projects.create(self.project, default_domain)

        users = keystone_client.users.list()
        for user in users:
            if self.name != user.name:
                continue
            else:
                user_obj = user
                break
        else:
            user_obj = keystone_client.users.create(self.name, password=self.password, domain=default_domain,
                                                    default_project=project_obj)

        ras = keystone_client.role_assignments.list(user=user_obj, project=project_obj)

        if ras:
            current_role_id = ras[0].role['id']
            for role in roles:
                if role.id == current_role_id:
                    keystone_client.roles.revoke(role, user=user_obj, project=project_obj)
                    break

        keystone_client.roles.grant(role_obj, user=user_obj, project=project_obj)


def read_template_from_excel(config_path):
    """
    read flavor configurations from excel
    :param config_path: path to excel configuration file
    :return: a list of flavors
    """

    if not os.path.exists(config_path):
        raise Exception("path: %s does not exist!", config_path)

    logger = get_logger()
    objects = []

    logger.info("read configuration from %s", config_path)
    wb = open_workbook(config_path)

    # by default, there is only a single sheet
    sheet = wb.sheets()[0]

    # ignore the first row
    for row in range(1, sheet.nrows):
        args = {}
        for col in range(sheet.ncols):

            # there should not be more than defined
            # number of columns
            if col > MAX_COLUMNS:
                break

            val = sheet.cell(row, col).value
            args[COLUME_NAME[col]] = val

        logger.info("args: %s", str(args))
        objects.append(User(**args))

    logger.info("retrieve %s records from %s", str(objects), config_path)
    # return a list of Flavors
    return objects


def init_client(credentials):
    # get logger
    logger = get_logger()

    # relation between variable name & corresponding environment variable
    required_fields = {'auth_url': 'OS_AUTH_URL',
                       'username': "OS_USERNAME",
                       'password': 'OS_PASSWORD',
                       'user_domain_name': "OS_USER_DOMAIN_NAME",
                       'project_name': "OS_PROJECT_NAME",
                       'project_domain_name': "OS_PROJECT_DOMAIN_NAME"
                       }

    # check & pop values from environment variable
    options = {}
    for key in required_fields.keys():
        if not credentials.get(key):
            value = os.environ[required_fields[key]]
            if not value:
                raise Exception("%s(%s) is missing" % (key, required_fields[key]))
            options.update({key: value})
        else:
            options.update({key: credentials.get(key)})

    logger.info("begin initializing nova client")
    loader = loading.get_plugin_loader('v3password')
    auth = loader.load_from_options(**options)
    sess = session.Session(auth=auth, verify=False)

    endpoint_type = credentials.get('endpoint_type', os.environ['OS_ENDPOINT_TYPE'])
    endpoint_type = endpoint_type if endpoint_type else "public"
    region_name = credentials.get('region_name', os.environ['OS_REGION_NAME'])
    region_name = region_name if region_name else "RegionOne"

    nova_client = client.Client(session=sess, endpoint_type=endpoint_type, region_name=region_name)
    logger.info("initialzing client completed successfully")

    # return a glance client
    return nova_client


def write_output_to_excel(users, filename):
    """
    write networks output to filename
    :param users:
    :param filename:
    :return:
    """

    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet("networks")

    attrs = ["service", "name", 'password', "project", "role"]

    for i in range(len(attrs)):
        sheet.write(0, i, attrs[i])

    for j in range(len(users)):
        for i in range(len(attrs)):
            sheet.write(1 + j, i, getattr(users[j], attrs[i], ''))

    workbook.save(filename)


def get_parser():
    import argparse

    parser = argparse.ArgumentParser(description='generate required flavors')
    parser.add_argument('-f', '--config', dest='config_path', required=True,
                        help='path to the configuration file')
    parser.add_argument('-d', '--debug', dest='debug', action='store_const', const=True,
                        default=False, help='enable debugging')
    parser.add_argument('-o', '--ouput', dest='output_file', default="networks.xls", help='write output to file')

    return parser.parse_args()


def main():
    """
    program entrance
    :return:
    """

    parser = get_parser()

    # setup loggings
    setup_logging(debug=parser.debug)

    # assemble flavor objects
    logger = get_logger()
    logger.info('configuration found at %s', parser.config_path)

    keystone_client = init_client({})

    users = read_template_from_excel(parser.config_path)
    for user in users:
        user.create_user(keystone_client)

    write_output_to_excel(users, parser.output_file)

    return 0


if __name__ == "__main__":
    exit(main())
