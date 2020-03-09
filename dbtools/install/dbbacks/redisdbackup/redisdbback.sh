#!/bin/bash

REDIS_CLI=/usr/local/redis/bin/redis-cli
REDISBACKUPDIR=/data/backup/full # 全库备份的目录
LOGS_DIR=/data/backup/logs # 日志目录

KEEP=7 # 保留几天全库备份

BACKUP_DATE=$(date +%y%m%d_%H_%M)
LOGFILE=$LOGS_DIR/redis_rdb_${BACKUP_DATE}.log

mkdir -p $REDISBACKUPDIR
mkdir -p $LOGS_DIR



####################backfupfiles clean================

find $REDISBACKUPDIR  -maxdepth 1 -mtime +$KEEP   -execdir rm -rf $REDISBACKUPDIR/{} \;

############################# redis rdb backup #######################

###获取当前主机运行的redis端口
for REDISPORT in `ps x|grep "redis-server *" |grep -v grep |awk -F ":" '{print $3}'`
do
	echo $REDISPORT
	DBPWD=`awk  '/^requirepass/{print $2}' /etc/redis/${REDISPORT}.conf|sed 's/"//g'`

	if test -z $DBPWD;then
        	OPT=" -p $REDISPORT  "
	else
        	OPT=" -p $REDISPORT -a $DBPWD "
	fi
	
        ###如果端口是主库备份数据
	if $REDIS_CLI $OPT   info|grep 'role:master' > /dev/null 2>&1;then
		echo " dbback  $REDISPORT"
		echo "[`date +"%Y-%m-%d %H:%M:%S"`] start rdb on $REDISPORT " >> $LOGFILE
		$REDIS_CLI $OPT  --rdb ${REDISBACKUPDIR}/${REDISPORT}_${BACKUP_DATE}.rdb >> $LOGFILE 2>&1
		FLAG1=1
		while [[ $FLAG1 == 1 ]]
		do
			if  $REDIS_CLI $OPT   info|grep 'rdb_bgsave_in_progress:0';then
				FLAG1=0
			fi
			sleep 1	
		done		

		echo "[`date +"%Y-%m-%d %H:%M:%S"`] end  rdb on $REDISPORT" >> $LOGFILE
		
		
	fi

	echo "[`date +"%Y-%m-%d %H:%M:%S"`] start bgrewrite on $REDISPORT " >> $LOGFILE
	$REDIS_CLI $OPT BGREWRITEAOF
	FLAG2=1
	while [[ $FLAG2 == 1 ]]
	do
		if  $REDIS_CLI $OPT   info|grep 'aof_rewrite_in_progress:0';then
			FLAG2=0
		fi
		sleep 1	
	done		
	echo "[`date +"%Y-%m-%d %H:%M:%S"`]  end  bgrewrite on $REDISPORT " >> $LOGFILE

done
