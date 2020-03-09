#!/bin/bash

####去掉save参数
#for i in `ls /etc/redis/*`;
#do
#	echo $i
#	DBPORT=`basename $i|awk -F '.' '{print $1}'`
#	sed -i  's/^save /#&/g' $i	
#	grep "^save" $i
#	echo "CONFIG set save '' "| /usr/bin/redislogin_${DBPORT} >/dev/null 2>&1
#	echo "CONFIG get  save  "| /usr/bin/redislogin_${DBPORT}

#done

#####修改redis配置的函数
config_set()
{
	for CONFIG in `ls /etc/redis/*`;
	do
		echo $CONFIG
		DBPORT=`basename $CONFIG|awk -F '.' '{print $1}'`
		sed -i "s/^$PARA .*/$PARA $PARA_VALUE/g" $CONFIG
		echo "配置文件配置"
		grep "^$PARA" $CONFIG
		
		echo "CONFIG set $PARA $PARA_VALUE "| /usr/bin/redislogin_${DBPORT} >/dev/null 2>&1
		echo "生效配置"
		echo "CONFIG get $PARA "| /usr/bin/redislogin_${DBPORT}
		echo ""
	done
}


####修改redis参数
CONF=(
	appendonly=yes
	maxmemory-policy=volatile-lru
	auto-aof-rewrite-min-size=10737418240
	auto-aof-rewrite-percentage=0
)

####循环修改redis参数
for LINE in ${CONF[@]}
do
	PARA=`echo ${LINE} | awk -F'=' '{print $1}'` 
	PARA_VALUE=`echo ${LINE} | awk -F'=' '{print $2}'`

	echo $PARA ${PARA_VALUE}
	config_set
	echo ""
done

