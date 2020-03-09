#!/bin/bash

check_raidisk(){
if [ ! -f /data/.raidiskstatus ];then
   touch /data/.raidiskstatus
fi

CMD=`which megaclisas-status`
$CMD --notemp|awk /c0u1p/ >/data/.raidiskstatus
SUM=`cat /data/.raidiskstatus|wc -l`
fail_times=0
rebuilding=0
ok_times=0
for i in `seq $SUM`
do
sed -n "${i}p" /data/.raidiskstatus|grep Online >/dev/null
if [ $? -eq 0 ];then
    let ok_times=$ok_times+1
fi
sed -n "${i}p" /data/.raidiskstatus|grep Rebuilding >/dev/null
if [ $? -eq 0 ];then
    let rebuilding=$rebuilding+1
fi
sed -n "${i}p" /data/.raidiskstatus|grep Failed >/dev/null
if [ $? -eq 0 ];then
    let fail_times=$fail_times+1
fi
done

echo "$ok_times $rebuilding $fail_times $SUM" >/data/.raidiskstatus
#if [ $1 == "ok" ];then
#    echo $ok_times
#elif [ $1 == "fail" ];then
#    echo $fail_times
#elif [ $1 == "sum" ];then
#    echo $SUM
#else
#    echo "$1 is not suport,please ok,fail,sum"
#fi
}
#check_raidisk $1
check_raidisk
