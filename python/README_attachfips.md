# Attach floating ip

## Intro
There are some instances that were attacked. We want to check security
issues throuth floating ips.

## Proposal
One dedicated server is the security device for scanning security issues.
This server uses one network connected the network for floating ip.
So tenant instances must have one floating ip.
Notes:
* Attach a floating ip if tenant instance has no one
* Detach the floating ip after the scanning
* Test linking between floating ip and security device's ip

