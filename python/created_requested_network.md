# CREATED DESIRED NETWORK

## INTRODUCTION

* Setup parser as well as logging configurations
  * parser configurations
  * logger format
* Read a list of networks from a excel doc
  * validate input values before tagging
* Create network one by one
  * use provider:physical_network=physnet1
  * router:external=True, provider:network_type=vlan, shared=True
  * pass in network name, subnet name, cidr, ...
  * disable dhcp? disable gw? use dns nameservers?
  * ip(allocation) pool? [{"start": xxx, "end": xxx}, ...]
* Exception handling

## TABLE STRUCTURE

| service | network name | subnet name | cidr | ip pool | vlan id | disable dhcp | disable gateway | dns | host routes |
|---|---|---|---|---|---|---|---|---|---|

## RUN

```bash
./create_requested_network -f ${PATH_TO_CONFIGURATION}
```
