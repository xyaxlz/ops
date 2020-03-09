#!/bin/bash

flumePath="/data/htdocs/dd.panda.tv.flume/apache-flume-1.6.0-bin"
flumeConfigPath="/data/htdocs/dd.panda.tv.flume/config_dd.panda.tv"
logPath="/data/logs/flume"
supervisorcnf=/etc/supervisor.d/flume_mulit.ini
>$supervisorcnf

while read LINE
do
if [ ${LINE} ];then

    program=`echo $LINE|sed 's/.conf//g'`

    echo "[program:$program]"                     >> $supervisorcnf
    echo "user=root"                              >> $supervisorcnf
    echo "command=${flumePath}/bin/flume-ng agent -n a1 -c ${flumePath}/conf -f ${flumeConfigPath}/${LINE} -Dflume.root.logger=INFO,console" >> $supervisorcnf
    echo "numprocs=1"                             >> $supervisorcnf
    echo "exitcodes=0"                            >> $supervisorcnf
    echo "autorestart=unexpected"                 >> $supervisorcnf
    echo "redirect_stderr=true"                   >> $supervisorcnf
    echo "minfds=327680"                          >> $supervisorcnf
    echo "stdout_logfile=${logPath}/${LINE}.log"  >> $supervisorcnf
    echo ""                                       >> $supervisorcnf

    multiprogram="$multiprogram,$program"

fi

done  < ${flumeConfigPath}/flume.multiprocess.conf

multiprogram=`echo $multiprogram|sed 's/,//'`
echo "[group:flume.multi]"                        >> $supervisorcnf
echo "programs=$multiprogram"                     >> $supervisorcnf
echo "priority=999"                               >> $supervisorcnf

