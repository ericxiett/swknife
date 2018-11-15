#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging


def setup_logging():
    logging.basicConfig(level=logging.INFO)


class Flavor(object):
    """
    flavor object
    """

    def __init__(self, name, cpu, memory, disk, spec):
        """
        initialize object
        :param name: service name
        :param cpu:  cpu number
        :param memory: memory size (in GB)
        :param disk:  hdd size (in GB)
        :param spec: specs no idea its difference between cpu things
        """

        self.name = name
        self.cpu = cpu
        self.memory = memory
        self.disk = disk

        # fixme spec might be a list of string
        if type(spec) == 'str':

            # string::split will return a list
            # make sure that utf-8 characters will not report error
            self.spec = spec.replace('，', ',').split(',')
        else:
            self.spec = spec

    def __repr__(self):
        """
        customize string representation
        :return:
        """

        template = "%s_%sC%sG%sG_%s"
        return template % (self.name, self.cpu, self.memory, self.disk, "_".join(self.spec))


def read_template(config_path):

    # return a list of Flavors
    return []


def create_flavors(glance_client, flavors):
    """
    create all required flavors
    :return:
    """

    return


def init_glance_client(credentials):

    glance_client = None

    # return a glance client
    return glance_client


def main():
    """
    program entrance
    :return:
    """

    args = sys.argv

    return 0


if __name__ == "__main__":
    exit(main())
