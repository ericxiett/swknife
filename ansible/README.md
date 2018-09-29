# Ansible scripts

## Configure project quota

### Install
* Find one vm or dedicated server that can link OpenStack API
* Install dependencies(example on ubuntu 16.04)
    ``` bash
    # Install ansible
    $ add-apt-repository ppa:ansible/ansible-2.4
    $ apt update
    $ apt install ansible
    # Add Pike repository
    $ add-apt-repository cloud-archive:pike
    $ apt update
    # Install openstacksdk,os-client-config,shade
    $ apt install python-openstacksdk python-os-client-config python-shade
    ```
* Configure clouds.yaml
    ``` bash
    $ mkdir -p /etc/openstack
    $ vim /etc/openstack/clouds.yaml
    clouds:
      rdenv:
        auth:
          username: << username >>
          password: << password >>
          project_name: << project >>
          auth_url: << url >>
          domain_id: << domain >>
        region_name: << region >>
        verify: False
        identity_api_version: 3
    # Replace related variables
    ```
### Use
``` bash
$ git clone https://github.com/ericxiett/swknife.git
$ cd swknife/ansible
$ ansible-playbook sit-conf-project-quota.yml
```
