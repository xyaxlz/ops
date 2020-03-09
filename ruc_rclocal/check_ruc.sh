#!/bin/bash
#
#
#
# check uid (should be root)
if [ `id -u` != 0 ];then
    echo "this script should be run as root only!"
    exit 1
fi

USER=root
HOSTNAME=`hostname`
PWD=`which pwd`



function sedmsg(){
	echo "ruc service was down"|mail -s "$HOST $SRV_NAME" root@`hostname`
}

function projstart(){
	# 重启 Supervisor
	supervisorctl start all
	# 重启 项目
        RG_ROOT=/home/q/tools/rigger
        srg='/home/q/tools/rigger/rigger'
	cd /home/q/system/ruc
	sudo $srg reconf,restart
	sleep 1
}


function ruc(){
`which curl` --silent -H "Host:u.pdtv.io" "http://127.0.0.1:8360/profile/getProfileByRid?rid=3009994" >/dev/null
if [ $? -ne 0 ];then
	killall nginx
	killall nginx
	sedmsg
fi
}


function wruc(){
`which curl` --silent -H "Host:u.panda.tv" "https://127.0.0.1/ajax_aeskey" >/dev/null
if [ $? -ne 0 ];then
	killall nginx
	killall nginx
	sedmsg
fi
}


function villa(){
`which curl` --silent -H "Host:u.panda.tv" "https://127.0.0.1/ajax_aeskey" >/dev/null
if [ $? -ne 0 ];then
	killall nginx
	killall nginx
	sedmsg
fi
}

source /etc/profile

case "$1" in
    ruc|wruc)
        projstart
        $1
        ;;
    *)
	echo $"Usage: $0 {ruc wruc}"
	exit 1
	;;
esac

