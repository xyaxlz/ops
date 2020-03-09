#!/bin/bash

dnsiparr=(
'10.110.20.254 badge.pdtv.io'
'10.110.21.0 badge.pdtv.io'
'10.110.20.255 badge.pdtv.io'
'10.110.21.1 badge.pdtv.io'
)

dns=`echo  ${dnsiparr[0]} |awk '{print $2}'`
sum=${#dnsiparr[@]}
num=`hostname |grep -Eo '[0-9]+'`
i=$(($num % $sum))
dnsip=${dnsiparr[$i]}
sed -i '/'"$dns"'/d' /etc/hosts
echo ${dnsip} >> /etc/hosts
