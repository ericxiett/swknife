# Change external gateway of vrouter

## Intro
Due to business demand, need to change the subnet of floating ip.
For existing VPC, the ext-gw of VR MUST be modified to the new network
of floating ip.

## Steps
1. Get all instances of vpcs(vxlan network) and floating ips
2. Disassociate floating ips and release them
3. Clear ext-gw of VR
4. Add new ext-gw of VR
5. Allocate floating ips and associate them to instances

## Backup
Use xls to backup vpcs and floating ips
Use xls to record new vr info(extgw: port-id, gwip)
