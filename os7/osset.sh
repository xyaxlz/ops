#!/bin/bash

yum install net-tools  vim sysstat python  ntp -y
yum remove firewalld -y
yum install iptables-services -y
systemctl stop iptables

#sudo sed -i 's/ZONE="UTC"/ZONE="Asia\/Shanghai"/g' /etc/sysconfig/clock
#sudo cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

sudo useradd  -u 1052 -p '$6$YSx.aZq.$gtB/HZd3O/OCCLSIgpFwooAhIeKv6YZ2t9AyW9gxPIxkIs3XqPvDdUpiolQRJwgYSMkEg2ErJS0LwZqlgluQE.'  liqingbin
sudo su - root -c  'echo "liqingbin  ALL=(ALL)    ALL" >> /etc/sudoers'

sudo useradd  -u 1032 -p '$6$q.KpZhmm$OGLtqCZOOXrGnNIU317UWvlSK6khoucC/iBe5gosdIVycjY9Z8zAwSHFL6mgj8VR1ANRUMmHIxKyL3wpveMHn/'  liufeng
sudo su - root -c  'echo "liufeng  ALL=(ALL)    ALL" >> /etc/sudoers'

sudo useradd  -u 1018 -p '$6$58jCBaD0$aNxAaEVqbIONWphyACWr4GnLCMLKS6MqhUHYn0RwZw7SE/InPUr7HiB/uqmGBOYUK20Oo2wlfyvS5hDV3ingJ/'  yangwuming
sudo su - root -c  'echo "yangwuming  ALL=(ALL)    ALL" >> /etc/sudoers'

#sudo sed -i '/^PasswordAuthentication no/ s/^/#/g' /etc/ssh/sshd_config
#sudo /etc/init.d/sshd restart

sed -i  's/^#UseDNS yes/UseDNS no/g' /etc/ssh/sshd_config
sed -i  's/^GSSAPIAuthentication yes/GSSAPIAuthentication no/g' /etc/ssh/sshd_config
sudo /etc/init.d/sshd restart

sed -i  's/^SELINUX=enforcing/SELINUX=disabled/g'  /etc/selinux/config
