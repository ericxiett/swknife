#!/usr/bin/env bash

set -ex

. /root/keystonercv3

openstack compute service list

openstack network agent list

openstack volume service list
