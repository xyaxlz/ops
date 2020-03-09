#!/bin/bash

dnsiparr=(
'10.110.16.126  villa.pdtv.io'
'10.110.16.127 villa.pdtv.io'
'10.110.17.134 villa.pdtv.io'
'10.110.17.135 villa.pdtv.io'
'10.110.18.2 villa.pdtv.io'
'10.110.20.166 villa.pdtv.io'
'10.110.20.162 villa.pdtv.io'
'10.110.20.163 villa.pdtv.io'
'10.110.20.165 villa.pdtv.io'
'10.110.20.164 villa.pdtv.io'
)

dns=`echo  ${dnsiparr[0]} |awk '{print $2}'`
sum=${#dnsiparr[@]}
num=`hostname |grep -Eo '[0-9]+'`
i=$(($num % $sum))
dnsip=${dnsiparr[$i]}
sed -i '/'"$dns"'/d' /etc/hosts
echo ${dnsip} >> /etc/hosts
