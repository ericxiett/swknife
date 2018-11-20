#CREATE CINDER_VOLUME_TYPES 

1.Edit cinder_volume_type config file(XLS_file)，then put them in the root directory
    * To run this script，Commands need to follow the format below
        " python test.py volume_type.xlsx"
2.Before create new cinder_volume_types,we need init enivorment by deleting exited volume_types
3.For the volume_types that have been attatched on volumes, it's necessary to rename them first
4.The metadata back_end_name has been bound with ceph

* It's the original version ,with many exting bugs that not be found。
* To run this script,make sure that the following modules have been installed:
  * sys, os, xlrd, random, string, keystoneauth1, cinderclient