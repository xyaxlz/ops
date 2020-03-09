#!/bin/bash

ipaddr="10.20.0.61"
bond_type="bond4"
bond_opt="mode=802.3ad miimon=100 lacp_rate=fast"



[ "zz$1" == "zz" ] && exit 2
ethconf="/etc/sysconfig/network-scripts/ifcfg-"
bond_dev="$ethconf$bond_type"
for eth in $@
do
	ethdev="$ethconf$eth"
	echo "DEVICE=$eth" > $ethdev
	echo "NAME=$eth" >> $ethdev
	echo "BOOTPROTO=none" >> $ethdev
	echo "MASTER=$bond_type" >> $ethdev
	echo "SLAVE=yes" >> $ethdev
done
echo "DEVICE=$bond_type
NAME=$bond_type
TYPE=Bond
BONDING_MASTER=yes
IPADDR=$ipaddr
GATEWAY=10.20.0.1
NETMASK=255.255.252.0
PEERDNS=yes
ONBOOT=yes
BOOTPROTO=static" > $bond_dev
#echo "BONDING_OPTS=\"$bond_opt\"" >> $bond_dev
echo "nameserver 10.20.0.10" > /etc/resolv.conf
