# CREATED DESIRED NETWORK

1. Setup parser as well as logging configurations
  * parser configurations
  * logger format
2. Read a list of networks from a excel doc
  * validate input values before tagging
3. Create network one by one
  * use provider:physical_network=physnet1
  * router:external=True, provider:network_type=vlan, shared=True
  * pass in network name, subnet name, cidr, ...
  * disable dhcp? disable gw? use dns nameservers?
  * ip(allocation) pool?
4. Exception handling