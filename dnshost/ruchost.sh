#!/bin/bash

dnsiparr=(
'10.110.16.131 count.pdtv.io'
'10.110.16.130 count.pdtv.io'
'10.110.17.138 count.pdtv.io'
'10.110.17.139 count.pdtv.io'
'10.110.17.140 count.pdtv.io'
'10.110.17.141 count.pdtv.io'
'10.110.17.142 count.pdtv.io'
'10.110.17.143 count.pdtv.io'
'10.110.17.144 count.pdtv.io'
'10.110.17.145 count.pdtv.io'
)

dns=`echo  ${dnsiparr[0]} |awk '{print $2}'`
sum=${#dnsiparr[@]}
num=`hostname |grep -Eo '[0-9]+'`
i=$(($num % $sum))
dnsip=${dnsiparr[$i]}
sed -i '/'"$dns"'/d' /etc/hosts
echo ${dnsip} >> /etc/hosts
