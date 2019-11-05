#!/bin/bash

set -x

VMNAME=$1
vmuuid=$(uuidgen)

cp /usr/share/AAVMF/AAVMF_VARS.fd /var/lib/libvirt/qemu/nvram/${VMNAME}_VARS.fd

mkdir -p /var/lib/libvirt/images/${VMNAME}
cd /var/lib/libvirt/images/${VMNAME}
qemu-img create -f qcow2 ${VMNAME}-data.qcow2 60G
cp /opt/vms/system_docker.qcow2 system.qcow2

#cp /var/lib/libvirt/qemu/nvram/slave10_VARS.fd  /var/lib/libvirt/qemu/nvram/${VMNAME}_VARS.fd

cat >/var/lib/libvirt/images/${VMNAME}/${VMNAME}.xml<<EOF
<domain type='kvm'>
  <name>${VMNAME}</name>
  <uuid>${vmuuid}</uuid>
  <memory unit='KiB'>8388608</memory>
  <currentMemory unit='KiB'>8388608</currentMemory>
  <vcpu placement='static'>4</vcpu>
  <os>
    <type arch='aarch64' machine='virt-2.11'>hvm</type>
    <loader readonly='yes' type='pflash'>/usr/share/AAVMF/AAVMF_CODE.fd</loader>
    <nvram>/var/lib/libvirt/qemu/nvram/${VMNAME}_VARS.fd</nvram>
    <boot dev='hd'/>
  </os>
  <features>
    <acpi/>
    <apic/>
    <gic version='3'/>
  </features>
  <cpu mode='host-passthrough' check='none'>
    <topology sockets='2' cores='2' threads='1'/>
  </cpu>
  <clock offset='utc'>
    <timer name='pit' tickpolicy='delay'/>
    <timer name='rtc' tickpolicy='catchup'/>
  </clock>
  <on_poweroff>destroy</on_poweroff>
  <on_reboot>restart</on_reboot>
  <on_crash>destroy</on_crash>
  <devices>
    <emulator>/usr/bin/qemu-system-aarch64</emulator>
    <disk type='file' device='disk'>
      <driver name='qemu' type='qcow2' cache='none'/>
      <source file='/var/lib/libvirt/images/${VMNAME}/${VMNAME}-data.qcow2'/>
      <target dev='vdb' bus='virtio'/>
      <address type='virtio-mmio'/>
    </disk>
    <disk type='file' device='disk'>
      <driver name='qemu' type='qcow2' cache='none'/>
      <source file='/var/lib/libvirt/images/${VMNAME}/system.qcow2'/>
      <target dev='vda' bus='virtio'/>
      <address type='virtio-mmio'/>
    </disk>
    <controller type='usb' index='0' model='qemu-xhci'>
      <address type='pci' domain='0x0000' bus='0x02' slot='0x00' function='0x0'/>
    </controller>
    <controller type='pci' index='0' model='pcie-root'/>
    <controller type='pci' index='1' model='pcie-root-port'>
      <model name='pcie-root-port'/>
      <target chassis='1' port='0x8'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x01' function='0x0' multifunction='on'/>
    </controller>
    <controller type='pci' index='2' model='pcie-root-port'>
      <model name='pcie-root-port'/>
      <target chassis='2' port='0x9'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x01' function='0x1'/>
    </controller>
    <controller type='pci' index='3' model='pcie-root-port'>
      <model name='pcie-root-port'/>
      <target chassis='3' port='0xa'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x01' function='0x2'/>
    </controller>
    <controller type='pci' index='4' model='pcie-root-port'>
      <model name='pcie-root-port'/>
      <target chassis='4' port='0xb'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x01' function='0x3'/>
    </controller>
    <controller type='pci' index='5' model='pcie-root-port'>
      <model name='pcie-root-port'/>
      <target chassis='5' port='0xc'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x01' function='0x4'/>
    </controller>
    <controller type='pci' index='6' model='pcie-root-port'>
      <model name='pcie-root-port'/>
      <target chassis='6' port='0xd'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x01' function='0x5'/>
    </controller>
    <controller type='pci' index='7' model='pcie-root-port'>
      <model name='pcie-root-port'/>
      <target chassis='7' port='0xe'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x01' function='0x6'/>
    </controller>
    <interface type='bridge'>
      <source bridge='br-mgt'/>
      <model type='virtio'/>
      <mtu size='1500'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x00' function='0x1'/>
    </interface>
    <interface type='bridge'>
      <source bridge='br-ctl'/>
      <model type='virtio'/>
      <mtu size='1500'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x00' function='0x2'/>
    </interface>
    <interface type='bridge'>
      <source bridge='br-sdata'/>
      <model type='virtio'/>
      <mtu size='1500'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x00' function='0x3'/>
    </interface>
    <interface type='bridge'>
      <source bridge='br-storpub'/>
      <model type='virtio'/>
      <mtu size='1500'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x00' function='0x4'/>
    </interface>
    <input type='tablet' bus='usb'>
      <address type='usb' bus='0' port='1'/>
    </input>
    <input type='keyboard' bus='usb'>
      <address type='usb' bus='0' port='2'/>
    </input>
    <graphics type='vnc' port='-1' autoport='yes' listen='0.0.0.0'>
      <listen type='address' address='0.0.0.0'/>
    </graphics>
    <video>
      <model type='virtio' heads='1' primary='yes'/>
      <address type='pci' domain='0x0000' bus='0x05' slot='0x00' function='0x0'/>
    </video>
    <memballoon model='virtio'>
      <stats period='10'/>
      <address type='pci' domain='0x0000' bus='0x04' slot='0x00' function='0x0'/>
    </memballoon>
  </devices>
</domain>
EOF

virsh define  /var/lib/libvirt/images/${VMNAME}/${VMNAME}.xml
virsh autostart ${VMNAME}
virsh start ${VMNAME}