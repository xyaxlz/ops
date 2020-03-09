#!/bin/bash
#20160111
ARG1_HOSTNAME=$1
SED_BIN=`which sed`
EXIT4=`which mkfs.ext4`
FORMAT='/sbin/mkfs.xfs -f'
TAR_BIN=`which tar`
MOUNT_BIN=`which mount`
RSYNC_BIN=`which rsync`
UMOUNT_BIN=`which umount`

[ "zz$ARG1_HOSTNAME" == "zz" ] && echo "init (failed)" && exit 1

echo "+host"
echo '127.0.0.1 localhost' > /etc/hosts
echo '::1         localhost localhost.localdomain localhost6 localhost6.localdomain6'  >> /etc/hosts

#/etc/sysconfig/network
$SED_BIN -i '/^HOSTNAME=/d' /etc/sysconfig/network
echo "HOSTNAME=$ARG1_HOSTNAME" >>/etc/sysconfig/network
grep "$ARG1_HOSTNAME" /etc/sysconfig/network >/dev/null 2>&1
[ $? -eq 0 ] &&echo "++hostname fix"
hostnamectl  set-hostname $ARG1_HOSTNAME


#/etc/hosts
grep $ARG1_HOSTNAME /etc/hosts >/dev/null 2>&1
[ $? -ne 0 ] && {
	sed -i "0,/^127.0.0.1/{//s/.*/& $ARG1_HOSTNAME/}" /etc/hosts 
	echo "++hosts fix"
}


echo "+dns"
echo "search bjza.pdtv.it" > /etc/resolv.conf
echo "options timeout:1 attempts:1 rotate" >> /etc/resolv.conf
echo "nameserver 10.120.254.94" >> /etc/resolv.conf
echo "nameserver 10.120.254.94" >> /etc/resolv.conf

for u in `ls /home`
do 
	authkey="/home/$u/.ssh/authorized_keys"
	[ -f "$authkey" ]&&chmod 600 $authkey
done

#/dev/vdb

formatDisk(){
		DISK=$1
		MOUNTPOINT=$2
		mkdir -p $MOUNTPOINT
		ls $DISK > /dev/null
		[ $? -ne 0 ] && echo "$DISK (is not exit!)" &&exit 1
		$MOUNT_BIN -v |grep $DISK >/dev/null 2>&1
        	[ $? -eq 0 ] && echo "$DISK (already mounted !)" &&exit 1
		$MOUNT_BIN -v |grep $MOUNTPOINT >/dev/null 2>&1
        	[ $? -eq 0 ] && echo "$MOUNTPOINT (already mounted !)" &&exit 1
		#format
		$FORMAT $DISK
		[ $? -ne 0 ] && echo "$FORMAT  (format failed)" &&exit 1
		grep $DISK /etc/fstab >/dev/null 2>&1
		[ $? -ne 0 ] && {
		echo "$DISK $MOUNTPOINT xfs rw,noatime,nobarrier 0 0" >>/etc/fstab
		echo "fstab fix"
		}
}

formatDisk /dev/xvdb /data
#formatDisk /dev/vdc /disk2
#formatDisk /dev/vdd /disk3
#formatDisk /dev/vde /disk4


############### swap ####################
newswap="/data/mem.swap.8G"
[ -f "$newswap" ]&& exit 0 
/bin/dd if=/dev/zero of=$newswap bs=1024 count=8000000
/sbin/mkswap $newswap
/sbin/swapon $newswap
grep "$newswap" /etc/fstab >/dev/null 2>&1
[ $? -ne 0 ] && echo "/data/mem.swap.8G none swap defaults 0 0" >> /etc/fstab




/usr/sbin/ntpdate 0.asia.pool.ntp.org
hwclock --hctosys --localtime


echo "ctrl + c stop"
sleep 5
sleep 5
reboot

