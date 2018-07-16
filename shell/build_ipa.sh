#!/bin/bash

set -ex

pypi_repo=https://pypi.tuna.tsinghua.edu.cn/simple/

# Install virtual env
yum install -y python-virtualenv
virtualenv dib-virtualenv

# Install dib
. dib-virtual/bin/activate
pip install -i $pypi_repo diskimage-builder

# Env variables
export DIB_DEV_USER_PWDLESS_SUDO="yes"
export DIB_DEV_USER_USERNAME="inspur"
export DIB_DEV_USER_PASSWORD="Lc13yfwpW"
export DIB_PYPI_MIRROR_URL="$pypi_repo"

disk-image-create ironic-agent centos7 install-static devuser epel pypi package-installs dhcp-all-interfaces -o deploy-latest
