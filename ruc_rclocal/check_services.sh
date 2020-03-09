#!/bin/bash
#
#author by zcx
#    20180326
#
# Source function library.
. /etc/rc.d/init.d/functions


# ----
# main
# ----
# check uid (should be root)
if [ `id -u` != 0 ];then
    echo "this script should be run as root only!"
    exit 1
fi

#send msg
function send_msg(){
        HOST=`hostname`
        SRV_NAME="$1"
        ps -ef|grep -v grep|grep -i $SRV_NAME >/dev/null 2>&1
        if [ $? -eq 0 ];then
                MSG=`echo $(date +%F\|%T\|%N) $HOST $SRV_NAME service is down!!! try $NUM times start $SRV_NAME was succeed!`
        else
                MSG=`echo $(date +%F\|%T\|%N) $HOST $SRV_NAME service is down!!! try $NUM times start $SRV_NAME was failed!`
        fi
        echo $MSG|mail -s "$HOST $SRV_NAME" root@$HOST
}


#send msg times
function warn_msg(){
        SRV_NAME="$1"
        case $NUM in
        1 | 2 | 3 | 4 | 5 )
        send_msg $SRV_NAME ;;
         *) echo -n "an unknown number off";;
        esac
}

#restart cmd
function rs_cmd(){
    SRV_NAME="$1"
    `which systemctl` start $SRV_NAME
}


#check services
function chk_srv(){
    SRV_NAME="$1"
    if [ $SRV_NAME == "zabbix-agent" ];then
          ps -ef|grep -v grep|grep -i zabbix_agentd >/dev/null 2>&1
          mkdir -p /var/run/zabbix/
          chown zabbix.zabbix -R /var/run/zabbix/
    else
          ps -ef|grep -v grep|grep -i $SRV_NAME >/dev/null 2>&1
    fi
    
}

#set up what services name check
SRV_NAMES=( supervisord rsyncd postfix ntpd nscd syslog-ng zabbix-agent )

for SRV_NAME in  "${SRV_NAMES[@]}"
do
    chk_srv $SRV_NAME
    if [ $? -eq 0 ];then
        if [ -f /dev/shm/.$SRV_NAME ];then
            rm -f /dev/shm/.$SRV_NAME
        fi
    else
        #try to restarting srv
        rs_cmd $SRV_NAME
        chk_srv $SRV_NAME
        if [ $? -eq 0 ];then
            NUM=1
            send_msg $SRV_NAME
        else
            if [ -f /dev/shm/.$SRV_NAME ];then
                NUM=`cat /dev/shm/.$SRV_NAME`
                let NUM=NUM+1
                echo $NUM >/dev/shm/.$SRV_NAME
            else
                echo 1 >/dev/shm/.$SRV_NAME
                NUM=1
            fi
            warn_msg $SRV_NAME
        fi
    fi
done
