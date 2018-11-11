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
    $ apt install python-pip virtualenv
    $ virtualenv swknife-dev
    $ . swknife-dev/bin/activate
    $ pip install openstacksdk==0.9.17
    $ pip install os-client-config==1.28.0
    $ pip install shade==1.10.0
    ```
* Configure clouds.yaml
    ``` bash
    $ git clone https://github.com/ericxiett/swknife.git
    $ cd swknife/ansible
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
        identity_interface: internal
        volumev3_interface: internal
        compute_interface: internal
        network_interface: internal
        image_interface: internal
    # Replace related variables
    ```

### Use

```bash
ansible-playbook sit-conf-project-quota.yml
```

### Q && A

* The error was: AttributeError: 'OperatorCloud' object has no attribute 'get_volume_quotas'
A: shade >= 1.10.0
