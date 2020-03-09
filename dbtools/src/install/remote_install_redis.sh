#!/bin/bash

usage()
{
    cat <<EOF
Redis 安装脚本使用说明
安装数据库前请
Usage:$0 [OPTION] [str] 
   -h     help              
   -m     redis master 
   -s     redis slave
   -p     redis password
   -P     redis port
   -g     内存大小，单位g
   -t     uninstall default is install,
	  注意卸载后redis数据会被清空
   -f     不安装数据库只主从复制配置 

sh   remote_install_redis.sh -m rdb13v.infra.bjac.pdtv.it -s rdb14v.infra.bjac.pdtv.it -p xxx  -P 6953 -g 10 
sh   remote_install_redis.sh -m rdb13v.infra.bjac.pdtv.it -s rdb14v.infra.bjac.pdtv.it  -P 6953  -t uninstall   
EOF
exit
}
[ $# == 0 ] && usage 
MASTER=''
SLAVE=''
FLAG=0


while getopts ":m:s:p:P:t:g:fh" opts;do
  case $opts in
	h)
		usage
		;;
	m)
		MASTER=$OPTARG
		;;
	s)
		SLAVE=$OPTARG
		;;
	f)
		FLAG=1
		;;
	p)
		DBPWD=$OPTARG
		;;
	P)
		DBPORT=$OPTARG
		;;
	g)
		MEMG=$OPTARG
		;;
	t)
		TYPE=$OPTARG
		;;
	*)
		-$OPTARG unvalid
		usage;;
  esac
done

#echo $MASTER 
#echo $SLAVE 
#echo $FLAG
#echo $DBPWD
#echo $DBPORT

#echo $SLAVE

####检查端口号是否是数字
if ! expr $DBPORT + 0 &>/dev/null;then
        echo "$DBPORT is not number"    
        exit
fi



####把域名解析成ip

if [[ $MASTER != '' ]];then
	MASTER=`nslookup   $MASTER |tail -n 2|head -n 1|awk '{print $2}'`
fi


if [[ $SLAVE != ''  ]];then
	SLAVETMP=$SLAVE
	SLAVE=''
	for i in $SLAVETMP
	do
        	i=`nslookup   $i |tail -n 2|head -n 1|awk '{print $2}'`
        	SLAVE="$SLAVE $i"
	done
	
fi

#####卸载redis 
if [[ $MASTER != '' && $TYPE == 'uninstall'  ]];then
	echo "[`date +"%Y-%m-%d %H:%M:%S"`] start master uninstall redis on $MASTER"
	scp -r  redis $MASTER:/data/install/  
	ssh   $MASTER "cd /data/install/redis;sh install_instance.sh -t uninstall -P '$DBPORT' "
	echo "[`date +"%Y-%m-%d %H:%M:%S"`] end master uninstall redis on $MASTER"
fi

if [[ $SLAVE != '' && $TYPE == 'uninstall'  ]];then
	for i in $SLAVE
	do
		echo "[`date +"%Y-%m-%d %H:%M:%S"`] start slave uninstall redis on $i"
		scp -r  redis $i:/data/install/ 
		ssh   $i  "cd /data/install/redis;sh install_instance.sh -t uninstall  -P '$DBPORT'"
		echo "[`date +"%Y-%m-%d %H:%M:%S"`] end  slave uninstall redis on $i"
	done
fi

if [[ $TYPE == 'uninstall'  ]];then
	exit
fi


####检查数据库是否已经安装
if [[ $MASTER != '' && $FLAG != 1 ]];then
	
	ssh $MASTER "/usr/sbin/lsof -i:$DBPORT"
	if [[ $? == 0  ]];then
		echo -e "\033[31m  $MASTER redis 数据库已经存在  \033[0m"
		exit
	fi

fi

if [[ $SLAVE != '' && $FLAG != 1 ]];then
	
	i=''
	for i in $SLAVE
	do
		ssh $i "/usr/sbin/lsof -i:$DBPORT"
		if [[ $? == 0  ]];then
			echo -e "\033[31m  $i redis 数据库已经存在  \033[0m"
			exit
		fi
	done
fi

##安装redis
if [[ $FLAG != 1 ]];then
	echo "[`date +"%Y-%m-%d %H:%M:%S"`] start install master redis on $MASTER"
	scp -r  redis $MASTER:/data/install/
	ssh   $MASTER "cd /data/install/redis;sh install_instance.sh -t install  -p '$DBPWD' -P '$DBPORT' -g '$MEMG'"
	echo "[`date +"%Y-%m-%d %H:%M:%S"`] end install master redis on $MASTER"

	for i in $SLAVE
	do
		echo "[`date +"%Y-%m-%d %H:%M:%S"`] start slave install redis on $i"
		scp -r  redis $i:/data/install/
		ssh   $i  "cd /data/install/redis;sh install_instance.sh -t install  -p '$DBPWD' -P '$DBPORT' -g '$MEMG'"
		echo "[`date +"%Y-%m-%d %H:%M:%S"`] start slave install redis on $i"
	done
fi

##配置redis主从关系

echo "[`date +"%Y-%m-%d %H:%M:%S"`] start config master-salve"
if [[ $SLAVE != '' && $MASTER != ''  ]];then
	echo "MASTER: $MASTER"
	ssh  $MASTER "sed -i \"/^slaveof/d\"  /etc/redis/${DBPORT}.conf"
	ssh  $MASTER  "echo \"slaveof NO ONE\"| redis-cli -a '$DBPWD' -p '$DBPORT'"

	for i in $SLAVE
	do
		echo "SLAVE: $SLAVE"
		ssh   $i  "sed -i \"/^slaveof/d\"  /etc/redis/${DBPORT}.conf"
		ssh   $i  "sed -i \"/^#slaveof/a\slaveof  ${MASTER} ${DBPORT}\"  /etc/redis/${DBPORT}.conf"
        	ssh   $i  "echo \"slaveof  ${MASTER} ${DBPORT}\"| redis-cli -a '$DBPWD' -p '$DBPORT'"
	
	done

fi
echo "[`date +"%Y-%m-%d %H:%M:%S"`] end config master-salve"

