#!/bin/bash
#rm -rf /etc/yum.repos.d/*.repo

## copy
for f in `find copy/|grep -v repo`
do
	src=$f
	s=$(echo $src|sed 's/copy//g')
	[ -f "$f" ]&& cp -v $f $s 
done

#rm -rfv /etc/yum.repos.d/CentOS-PDTV.repo
#wget http://mirrors.163.com/.help/CentOS7-Base-163.repo -O /etc/yum.repos.d/Centos-163.repo
## yum install
yum -y groupinstall "Base" "Development tools" "Additional Development" "System administration tools" "Networking Tools" "Performance Tools" "Server Platform Development"
yum install -y libevent-devel lua-devel openssl-devel flex xz gettext-devel net-tools irqbalance
yum -y install pcre-devel openssl-devel gawk libxml2-devel curl-devel freetype-devel ncurses-devel libevent libevent-devel readline-devel boost-devel libuuid-devel zlib-devel ntp bzip2-devel net-snmp net-snmp-utils libjpeg-devel libpng-devel logwatch gperf expat-devel libmemcached-devel iptraf expect rrdtool screen tree dos2unix glib2-devel libesmtp-devel json-c-devel

systemctl stop firewalld
systemctl disable firewalld
yum remove firewalld -y
yum install iptables iptables-services -y

systemctl restart systemd-sysctl
systemctl restart irqbalance
systemctl enable irqbalance
systemctl disable tuned
systemctl enable iptables
