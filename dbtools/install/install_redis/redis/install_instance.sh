#!/bin/bash

usage()
{
    cat <<EOF
Redis 安装脚本使用说明
Usage:$0 [OPTION] [str] 
   -h     help              
   -t     install or uninstall
   -p     redis password
   -P     redis DBPORT
   -g     内存大小，单位g
   
   
EOF
exit
}
[ $# == 0 ] && usage

while getopts ":t:p:P:g:h" opts;do
  case $opts in
        h)
                usage
                ;;
        t)
                TYPE=$OPTARG
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
        *)
                -$OPTARG unvalid
                usage;;
  esac
done

if ! expr $DBPORT + 0 &>/dev/null;then
	echo "$DBPORT is not number"	
	exit
fi


if [[  $TYPE != 'install' &&  $TYPE != 'uninstall' ]];then
        echo "-t     install or uninstall"
	usage
fi




install()
{
	mkdir -p /data/redis/${DBPORT}/log/
	mkdir -p /data/redis/${DBPORT}/data/
	mkdir -p /etc/redis/

	\cp -f redis_init_script /etc/init.d/redis_${DBPORT}
	\cp -f redis.conf /etc/redis/${DBPORT}.conf
        \cp redislogin  /usr/bin/redislogin_${DBPORT}
	chmod +x  /usr/bin/redislogin_${DBPORT}

	sed -i "s/6379/${DBPORT}/g" /usr/bin/redislogin_${DBPORT}
	sed -i "s/6379/${DBPORT}/g" /etc/init.d/redis_${DBPORT}
	sed -i "s/6379/${DBPORT}/g" /etc/redis/${DBPORT}.conf

	if ! test -z $DBPWD;then
		 
		 sed -i "/^masterauth/d"  /etc/redis/${DBPORT}.conf
		 sed -i "/^requirepass/d"  /etc/redis/${DBPORT}.conf
		  
		 sed -i "/^#masterauth/a\masterauth ${DBPWD}"  /etc/redis/${DBPORT}.conf
		 sed -i "/^#requirepass/a\requirepass  ${DBPWD}"  /etc/redis/${DBPORT}.conf

	fi
	

	if ! test -z $MEMG;then
		sed -i  "s/^maxmemory .*/maxmemory ${MEMG}Gb/g" /etc/redis/${DBPORT}.conf	
	fi
        
	chmod +x /etc/init.d/redis_${DBPORT}
	chkconfig  --add redis_${DBPORT}
        chkconfig redis_${DBPORT}  on
	/etc/init.d/redis_${DBPORT} start 
}

uninstall()
{

	/etc/init.d/redis_${DBPORT} stop
 	chkconfig  --del redis_${DBPORT}
	rm -rf  /data/redis/${DBPORT}
	rm -f   /etc/init.d/redis_${DBPORT}
	rm -f   /etc/redis/${DBPORT}.conf
        rm -f   /usr/bin/redislogin_${DBPORT}

}

### install or uninstall
$TYPE

