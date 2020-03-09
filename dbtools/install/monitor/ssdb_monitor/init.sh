#!/bin/bash
sh zabbix_agent.install
\cp -rf  scripts/ /etc/zabbix/
\cp -rf  redis.conf /etc/zabbix/zabbix_agentd.d/
chmod +x /etc/zabbix/scripts/redis_info.sh
chmod +x /etc/zabbix/scripts/redis_port.py
chmod +s /bin/netstat
yum install python-simplejson -y
/etc/init.d/zabbix-agent restart
