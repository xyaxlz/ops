#!/bin/bash
port=$1
key=$2
args=""
password=`sed -n  '/^requirepass/p' /etc/redis/${port}.conf|head -n 1 |awk  '{print $2}'|sed 's/"//g'`

if test -z $DBPWD;then
	args="-a $password"
fi

if [[ $key == cpu ]];then
	 pid=`/bin/ps aux|grep redis-server  |grep $port|awk '{print $2}'`
	 /usr/bin/pidstat -p $pid  1 2 | tail -n 1 |awk '{print $6}'
	exit
fi


if [[ $key == cnf* ]];then
	key=`echo $key |sed 's/cnf//g'`
	echo "config get $key "|/usr/local/redis/bin/redis-cli  $args -p $port |tail -n 1
else
	echo info | /usr/local/redis/bin/redis-cli  $args  -p $port | grep $key|cut -d : -f2
fi

