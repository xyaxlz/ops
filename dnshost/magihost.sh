#!/bin/bash

dnsiparr=(
'10.110.16.197 magi.pdtv.io'
)

dns=`echo  ${dnsiparr[0]} |awk '{print $2}'`
sum=${#dnsiparr[@]}
num=`hostname |grep -Eo '[0-9]+'`
i=$(($num % $sum))
dnsip=${dnsiparr[$i]}
sed -i '/'"$dns"'/d' /etc/hosts
echo ${dnsip} >> /etc/hosts
