#!/bin/bash

dnsiparr=(
'10.110.19.155 relation.pdtv.io'
'10.110.19.156 relation.pdtv.io'
'10.110.19.157 relation.pdtv.io'
'10.110.19.158 relation.pdtv.io'
'10.110.19.159 relation.pdtv.io'
'10.110.19.160 relation.pdtv.io'
)

dns=`echo  ${dnsiparr[0]} |awk '{print $2}'`
sum=${#dnsiparr[@]}
num=`hostname |grep -Eo '[0-9]+'`
i=$(($num % $sum))
dnsip=${dnsiparr[$i]}
sed -i '/'"$dns"'/d' /etc/hosts
echo ${dnsip} >> /etc/hosts
