#!/bin/bash


#数据目录
dir="/data/server/codis3_drc/redis/data/"

#bin
bin="/data/server/codis3_drc/bin"

#备份目录
backup_dir="/data/backups/codis"

mkdir -p ${backup_dir}

hostIp=`/sbin/ifconfig -a |egrep 'bond|team' -A 3 |grep -v 127.0.0.1 |grep 'inet ' |awk '{print $2}'`
MYSQL="mysql -h 10.100.20.60 -udbms -pzybackup%126& --default-character-set=utf8 dbms "
dbback() {
    PORT=$1
    #global backup file name
    file_name="redis-${PORT}-dump.rdb"
    
    
    #execute backup
    if $bin/redis-cli -p ${PORT} "info" | grep "role:slave" > /dev/null 2>&1;then
	echo "[`date +"%Y-%m-%d %H:%M:%S"`] start rdb on $PORT "
        if $bin/redis-cli -p ${PORT} --rdb $backup_dir/$file_name.`date +%y%m%d%H%M` ;then
    		SQL="insert into codis_back (bakip,bakport ,flag,backtime) values('${hostIp}',$PORT,'sucess','`date +%y%m%d%H%M`')"
		$MYSQL -e "$SQL"
		echo "[`date +"%Y-%m-%d %H:%M:%S"`] end rdb sucess on $PORT "
	else
    		SQL="insert into codis_back (bakip,bakport ,flag,backtime) values('${hostIp}',$PORT,'fail','`date +%y%m%d%H%M`')"
		$MYSQL -e "$SQL"
		echo "[`date +"%Y-%m-%d %H:%M:%S"`] end rdb fail on $PORT "

	fi
    fi
}

for num in `ps aux|grep codis-server |grep -v sentinel |grep -v grep | awk -F ":" '{print $3}'`
do
	dbback $num
done
/usr/bin/find $backup_dir -name "redis-*-dump\.rdb\.*" -type f -ctime +1 | xargs -n 1 rm -f
