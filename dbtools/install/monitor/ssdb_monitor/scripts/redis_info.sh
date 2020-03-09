#!/bin/bash

port=$1
key=$2
#password=`sed -n  '/^requirepass/p' /etc/redis/${port}.conf|head -n 1 |awk  '{print $2}'`
 /usr/local/ssdb/ssdb-cli   -p $port info 2>/dev/null | grep $key|cut -d : -f2
