#!/bin/bash
for i in `ls /etc/redis/*`;
do
	echo $i
	
#	DBPORT=`basename $i|awk -F '.' '{print $1}'`
#	chmod +x /etc/init.d/redis_${DBPORT}
#	sed -i  '/^# chkconfig: 2345/d' /etc/init.d/redis_${DBPORT}
#	sed -i  '/^# as it/a# chkconfig: 2345 64 36' /etc/init.d/redis_${DBPORT}
#	chkconfig  --add redis_${DBPORT}
#        chkconfig redis_${DBPORT}  on
#	rm -f /usr/bin/redislogin
#	\cp redislogin  /usr/bin/redislogin_${DBPORT}
#	chmod +x  /usr/bin/redislogin_${DBPORT}
#	sed -i "s/6379/${DBPORT}/g" /usr/bin/redislogin_${DBPORT}
done
