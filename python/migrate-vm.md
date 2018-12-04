# MIGRATE VM

## USAGE

```bash
# to list all available options
./migrate-vm.py -h

# to provide excel formatted options
./migrate-vm.py -f ${PATH_TO_CONFIG}

# to direct output to desired file
./migrate-vm.py -o ${PATH_TO_OUTPUT}

# to disable preview mode and migrate vm
./migrate-vm.py --no-preview
```

## WORKFLOW

First, program will read candidates from input and try to get corresponding instnaces from openstack. It will try to get instances by name, then by id if former failed.

Secondly program will try to list enumerate all existing aggregates and construct relationships with all the hosts (hypervisors).

Then script will try to schedule all candidates to availably host aggregates in a greedy manner: it will compare them by free vcpus and available ram will be used as tie breaker if needed.

Dependending on whether **preview** mode is disabled, program will try to migrate instance to its scheduled destination. It will first try to live migrate instance if instnace is *active* or *puased*. And cold migrate if instance is not errored.

At last, output will be dumpped to an excel with each sheet stands for *inogre*, *preview*, *failed* and *error* instances.

## INPUT FORMAT

```raw
-------------------------------------
| instance name (instance id) | tag |
-------------------------------------
```


