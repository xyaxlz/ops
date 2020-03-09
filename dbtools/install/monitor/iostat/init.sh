#!/bin/bash
\cp dev-discovery.sh -f  /etc/zabbix/scripts/
chmod +x /etc/zabbix/scripts/dev-discovery.sh

\cp iostat-check.sh -f  /etc/zabbix/scripts/ 
chmod +x /etc/zabbix/scripts/iostat-check.sh

\cp iostat-cron.sh -f  /etc/zabbix/scripts/ 
chmod +x /etc/zabbix/scripts/iostat-cron.sh

\cp iostat-cron.conf -f /etc/cron.d/iostat-cron 


\cp iostat-params.conf -f /etc/zabbix/zabbix_agentd.d/
/etc/init.d/zabbix-agent restart

