#!/bin/bash

dnsiparr=(
'10.110.16.132  api.u.panda.tv'
'10.110.16.133  api.u.panda.tv'
'10.110.17.114  api.u.panda.tv'
'10.110.17.115  api.u.panda.tv'
'10.110.17.116  api.u.panda.tv'
'10.110.17.117  api.u.panda.tv'
'10.110.17.118  api.u.panda.tv'
'10.110.17.119  api.u.panda.tv'
'10.110.17.120  api.u.panda.tv'
'10.110.17.121  api.u.panda.tv'
'10.110.17.122  api.u.panda.tv'
'10.110.17.123  api.u.panda.tv'
'10.110.17.124  api.u.panda.tv'
'10.110.17.125  api.u.panda.tv'
'10.110.17.126  api.u.panda.tv'
'10.110.17.127  api.u.panda.tv'
'10.110.17.128  api.u.panda.tv'
'10.110.17.129  api.u.panda.tv'
'10.110.17.130  api.u.panda.tv'
'10.110.17.131  api.u.panda.tv'
'10.110.17.132  api.u.panda.tv'
'10.110.17.133  api.u.panda.tv'
)

dns=`echo  ${dnsiparr[0]} |awk '{print $2}'`
sum=${#dnsiparr[@]}
num=`hostname |grep -Eo '[0-9]+'`
i=$(($num % $sum))
dnsip=${dnsiparr[$i]}
sed -i '/'"$dns"'/d' /etc/hosts
echo ${dnsip} >> /etc/hosts
