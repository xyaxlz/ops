#!/bin/bash
rpm --import http://repo.zabbix.com/RPM-GPG-KEY-ZABBIX 
rpm -Uv  http://repo.zabbix.com/zabbix/2.4/rhel/6/x86_64/zabbix-release-2.4-1.el6.noarch.rpm 
yum clean all 
yum install zabbix-agent -y
mv  -f  /etc/zabbix/zabbix_agentd.conf /etc/zabbix/zabbix_agentd.confbak
echo 'PidFile=/var/run/zabbix/zabbix_agentd.pid'> /etc/zabbix/zabbix_agentd.conf
echo 'LogFile=/var/log/zabbix/zabbix_agentd.log'>> /etc/zabbix/zabbix_agentd.conf
echo 'LogFileSize=0'>> /etc/zabbix/zabbix_agentd.conf
echo 'Server=10.110.16.21,10.110.18.203'>> /etc/zabbix/zabbix_agentd.conf
echo 'ServerActive=10.110.16.21,10.110.18.203'>> /etc/zabbix/zabbix_agentd.conf
hostname=`hostname|awk -F '.' '{printf "%s_%s", $3,$1}'`
echo "Hostname=$hostname" >> /etc/zabbix/zabbix_agentd.conf
echo 'Include=/etc/zabbix/zabbix_agentd.d/'>> /etc/zabbix/zabbix_agentd.conf 
#yum  install  http://www.percona.com/downloads/percona-release/redhat/0.1-3/percona-release-0.1-3.noarch.rpm -y
rpm -e percona-zabbix-templates
wget http://www.percona.com/downloads/percona-release/redhat/0.1-3/percona-release-0.1-3.noarch.rpm
rpm -ivh percona-release-0.1-3.noarch.rpm
yum install percona-zabbix-templates php-mysql php -y
\cp -f  /var/lib/zabbix/percona/templates/userparameter_percona_mysql.conf  /etc/zabbix/zabbix_agentd.d/
sed -i 's/cactiuser/zabbix/g' /var/lib/zabbix/percona/scripts/ss_get_mysql_stats.php
mysql -h 127.0.0.1  --port 3306 -e "grant process,super,select on *.* to zabbix@127.0.0.1 identified by 'zabbix'"
mysql -h 127.0.0.1  --port 3306 -e "grant process,super,select on *.* to zabbix@localhost identified by 'zabbix'"
sed  -i  "s/HOME=~zabbix mysql -e 'SHOW SLAVE STATUS\\\G'/\/usr\/local\/mysql\/bin\/mysql  -h 127.0.0.1  --port 3306 -uzabbix -pzabbix -e 'SHOW SLAVE STATUS\\\G' 2> \/dev\/null /g" /var/lib/zabbix/percona/scripts/get_mysql_stats_wrapper.sh
sed -i "/^HOST=/ c HOST=127.0.0.1"  /var/lib/zabbix/percona/scripts/get_mysql_stats_wrapper.sh 
sed -i  's/\[ "$RES" = " Yes, Yes," \]/\[ "$RES" = " Yes, Yes," -o "$RES" = "" \]/g' /var/lib/zabbix/percona/scripts/get_mysql_stats_wrapper.sh
#sed  -i   's/^mysqli.default_socket =$/mysqli.default_socket =\/tmp\/mysql.sock/g' /etc/php.ini
/etc/init.d/zabbix-agent restart
