#!/bin/bash
sed -i "/^Server=/c\Server=10.110.18.203,10.110.16.21 " /etc/zabbix/zabbix_agentd.conf
sed  -i "/^ServerActive=/c\ServerActive=10.110.18.203,10.110.16.21 " /etc/zabbix/zabbix_agentd.conf
a=`hostname|awk -F '.' '{printf "%s_%s", $3,$1}'`
sed -i "/^Hostname=/c\Hostname=$a " /etc/zabbix/zabbix_agentd.conf
/etc/init.d/zabbix-agent restart
