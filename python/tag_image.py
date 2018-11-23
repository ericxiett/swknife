#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import subprocess,re

from keystoneauth1 import loading, session

# Global variables
from glanceclient import Client
import os
from xlrd import open_workbook


MAX_COLUMNS = 3
COLUME_NAME = ["image_uuid", "image_name", "image_tags"]

AUTH_URL='http://192.168.2.10:35357/v3'
USERNAME = 'admin'
PASSWORD = '89rqdHLMN5rm0x1P'
PROJECT_NAME = 'admin'
DOMAIN_NAME = 'Default'
DOMAIN_ID = 'default'
GLANCE_URL='http://192.168.2.10:9292'

def get_glance_client():
    loader = loading.get_plugin_loader('password')
    auth = loader.load_from_options(auth_url=AUTH_URL,
                                    username=USERNAME,
                                    password=PASSWORD,
                                    project_name=PROJECT_NAME,
                                    user_domain_name=DOMAIN_NAME,
                                    project_domain_name=DOMAIN_NAME)
    sess = session.Session(auth=auth)
    return Client('2',endpoint=GLANCE_URL,session=sess)

def read_config(config_path):
    if not os.path.exists(config_path):
        raise Exception("path: %s does not exist!", config_path)

    print("read configuration from %s" % (config_path))
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

            # fixme value might have letter like 'G'
            val = sheet.cell(row, col).value
            args[COLUME_NAME[col]] = val

        #logger.info("args: %s", str(args))
        print("args:%s" %args)
        #set image tags
        for tag in args.get('image_tags').split(','):

            update_image_tags(args.get('image_uuid'),tag)


def get_images():
    glance_client = get_glance_client()
    all_images = glance_client.images.list()
    #images object
    #return all_images
    for image in all_images:
        print( image.id,image.name,image.status,image.tags)

def get_id_byname(image_name):
    #by image name obtain imageid,exist the same name images
    image_id_list=[]
    glance_client = get_glance_client()
    all_images = glance_client.images.list()
    for image in all_images:
        if image.name == image_name:
            print("Image name:%s,id:%s" % (image_name,image.id))
            image_id_list.append(image.id)
    if len(image_id_list)== 0:
        print("Image name:%s,not found" % (image_name))
    return  image_id_list


def get_image_tags(image_id):
    glance_client = get_glance_client()
    image_tags = glance_client.images.get(image_id).get('tags')
    return image_tags

def update_image_tags(image_id,tag_name):
    #set image tags
    glance_client = get_glance_client()
    try:
        glance_client.image_tags.update(image_id,tag_name)
        print("set image:%s ,tag:%s successful" % (image_id,tag_name))
    except Exception:
        print("set image:%s ,tag:%s failure" % (image_id,tag_name))

def delete_image_tags(image_id,tag_name):
    #delete image tags
    glance_client = get_glance_client()
    try:
        glance_client.image_tags.delete(image_id,tag_name)
        print("delete image:%s ,tag:%s successful" % (image_id,tag_name))
    except Exception:
        print("delete image:%s ,tag:%s failure" % (image_id,tag_name))

def main():
    config_path="image_tags.xlsx"
    read_config(config_path)
    return 0


if __name__ == "__main__":
    exit(main())
