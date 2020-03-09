##客户客户端
/etc/zabbix/scripts/redis_port.py

#服务器端
zabbix_get   -s 10.110.16.239  -k redis.discovery
zabbix_get   -s 10.110.16.239  -k redis_stats[6083,blocked_clients]
