#!/bin/bash

#  usage:  script port :        script.sh 3306
#  writer:yangting
#  discript:use slave_hiearchy.py to print replication hierarchy tree of MySQL slaves 
#  version:1.0
function valid_ip()
{
    local  ip=$1
    local  stat=1

    if [[ $ip =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
        OIFS=$IFS
        IFS='.'
        ip=($ip)
        IFS=$OIFS
        [[ ${ip[0]} -le 255 && ${ip[1]} -le 255 \
            && ${ip[2]} -le 255 && ${ip[3]} -le 255 ]]
        stat=$?
    fi
    return $stat
}

if [[ "$#" !=  2 &&   "$#" != 4 ]]  
then
echo "usage:   script.sh -P port -D port"
exit 1
fi

declare -i port
declare -i dport

while getopts P:H:D: OPTION
do
   case "$OPTION" in
       P)port=$OPTARG
       ;;
       D)dport=$OPTARG
       ;;
       H)master_host=$OPTARG
       ;;
       *)
       echo "usage:   script.sh -P port" 2>&1
            exit 1
          ;;
   esac
done

if [ -z $dport ]
then 
host_ip=$master_host
valid_ip $master_host
if   valid_ip $master_host
then
host_ip=$master_host
else
host_ip=" db${master_host}v.infra.bjac.pdtv.it"
fi
/usr/local/bin/python2.7 /etc/db_tools/slave_hierarchy.py -P $port -H $host_ip
else
echo "the first port:$port"
host_ip=`host s"$port".mysql.m.com|grep -v 'alias'|awk '{print $NF}'|head -1`
/usr/local/bin/python2.7 /etc/db_tools/slave_hierarchy.py -P $port -H $host_ip
echo "             "
echo "the second dport :$dport"
d_ip=`host s"$dport"i.mars.grid.sina.com.cn|grep -v 'alias'|awk '{print $NF}'|head -1`
/usr/bin/python slave_hierarchy.py -P $dport -H $d_ip
fi
