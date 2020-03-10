#!/bin/bash

usage()
{
    cat <<EOF
Usage:$0 -t [master|slave] 
   -h     help              
   -p     mysql root用户密码 
   -P     数据库端口
EOF
exit
}
[ $# == 0 ] && usage 

DBPORT='3306'

while getopts ":h:p:P:" opts;do
  case $opts in
	h)
		usage
		;;
	p)
		DBPWD=$OPTARG
		;;
	P)

		DBPORT=$OPTARG
		;;
	*)
		-$OPTARG unvalid
		usage;;
  esac
done



####设置全局变量

MYSQLDIR=/usr/local/mysql/bin


###创建数据库安装目录
mkdir  -p /data/mysql/mysqldata/data    
mkdir  -p /data/mysql/mysqldata/tmp
mkdir  -p /data/mysql/mysqldata/ibdata
mkdir  -p /data/mysql/mysqllog/redolog
mkdir  -p /data/mysql/mysqllog/slowquery/
mkdir  -p /data/mysql/mysqllog/binlog/
mkdir  -p /data/mysql/mysqllog/relaylog/
chown mysql.mysql -R /data/mysql

###修改配置文件
\cp -f my.cnf /etc/my.cnf


sed -i "s/$DBPORT/3306/g" /etc/my.cnf

SERVER_ID=$(($((RANDOM%9000))+1000))
sed -i "s/server-id.*/server-id = $SERVER_ID/g" /etc/my.cnf

MEM1=`awk 'NR==1{print int($2/1024*0.6)}' /proc/meminfo`
BMEM1=`echo $MEM1|awk '{if($1 > 1024) {printf "%d%s" ,int($1/1024),"G" } else {printf "%d%s",($1),"M"} }'`
sed -i "/^innodb_buffer_pool_size/ c innodb_buffer_pool_size = ${BMEM1}" /etc/my.cnf

####初始化mysql
/usr/local/mysql/scripts/mysql_install_db  --datadir=/data/mysql/mysqldata/data/   --basedir=/usr/local/mysql    --user=mysql


####设置mysql自启动
\cp -f  /usr/local/mysql/support-files/mysql.server  /etc/init.d/mysqld
sed -i  's/^basedir=/basedir=\/usr\/local\/mysql/g' /etc/init.d/mysqld
sed -i "s/^datadir=/datadir=\/data\/mysql\/mysqldata\/data/g" /etc/init.d/mysqld
chmod +x /etc/init.d/mysqld
chkconfig  --add mysqld
chkconfig mysqld on

/etc/init.d/mysqld restart




####删除空账号，创建备份账号,设置root密码
$MYSQLDIR/mysql -S /tmp/mysql_${DBPORT}.sock  -e "delete from mysql.user where user='';"
$MYSQLDIR/mysql -S /tmp/mysql_${DBPORT}.sock   -e "delete from mysql.user where host='';"
$MYSQLDIR/mysql -S /tmp/mysql_${DBPORT}.sock   -e "GRANT SELECT,LOCK TABLES,RELOAD,SUPER,EVENT,EXECUTE ON *.* TO 'dbback'@'localhost' IDENTIFIED BY 'xxx';"
$MYSQLDIR/mysqladmin -S /tmp/mysql_${DBPORT}.sock   password  $DBPWD

if [[ $DBPWD == '' ]];then
       $MYSQLDIR/mysql -S /tmp/mysql_${DBPORT}.sock  -e "use mysql"
       FLAG=$?
else
       $MYSQLDIR/mysql -S /tmp/mysql_${DBPORT}.sock -uroot -p$DBPWD  -e "use mysql"
       FLAG=$?
fi


if [[ $FLAG == 0  ]];then
	echo -e "\033[31m  数据库安装完毕 \033[0m"  
	echo -e "\033[32m 1、安装脚本已经将mysql设为系统的自启动服务器 \033[0m"		  
	echo -e "\033[32m 2、mysql服务管理工具使用方法：/etc/init.d/mysqld  {start|stop|restart|reload|force-reload|status}  \033[0m"  
	echo -e "\033[32m 3、重开一个session，可使用mysql -S  /tmp/mysql.sock  -uroot -p 进入mysql。  \033[0m"  
else
	echo -e "\033[31m \033[05m 数据库安装失败 \033[0m" 
	exit 1
fi
