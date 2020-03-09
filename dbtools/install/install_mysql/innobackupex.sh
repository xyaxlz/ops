#!/bin/bash

PREFIX=PROD ##请修改

INNOBACKUPEX=/usr/bin/innobackupex
INNOBACKUPEXFULL=/usr/bin/innobackupex
MYCNF=/etc/my.cnf
USER='dbback'
PASSWORD='dbback'

FULLBACKUPDIR=/data/backup/full # 全库备份的目录
LOGS_DIR=/data/backup/logs # 日志目录

TMPFILE="/tmp/innobackupex-runner.$$.tmp"
KEEP=1 # 保留几天全库备份

BACKUP_DATE=$(date +%y%m%d_%H_%M)
LOGFILE=$LOGS_DIR/${PREFIX}_xtrabackup_${BACKUP_DATE}.log

mkdir -p $FULLBACKUPDIR
mkdir -p $LOGS_DIR



####################backfupfiles clean================
MKEEP=`echo ${KEEP}*60*24|bc`
find $FULLBACKUPDIR -maxdepth 1 -mmin +$MKEEP   -execdir rm -rf $FULLBACKUPDIR/{} \;

############################# innobackupex #######################
echo "[`date +"%Y-%m-%d %H:%M:%S"`] start innobackupex" >> $LOGFILE

$INNOBACKUPEXFULL --defaults-file=$MYCNF --user=$USER  --password=$PASSWORD --ftwrl-wait-timeout=300  $FULLBACKUPDIR > $TMPFILE 2>&1

if tail -1 $TMPFILE | grep 'completed OK!' ;then
        echo "[`date +"%Y-%m-%d %H:%M:%S"`] end innobackupex successfull" >> $LOGFILE
else

        echo "[`date +"%Y-%m-%d %H:%M:%S"`] end innobackupex fail" >> $LOGFILE
        exit
fi


##############################tar files ###########################
#cd $FULLBACKUPDIR
#THISBACKUP=`awk --  "/Backup created in directory/{split( \\\$0, p, \"'\" ) ; print p[2] }" $TMPFILE`
#THISBACKUP=`basename $THISBACKUP`
#TARNAME=$FULLBACKUPDIR/${PREFIX}_xtrabackup_${BACKUP_DATE}.tar.gz
#
#rm -f $TMPFILE
#
#echo "[`date +"%Y-%m-%d %H:%M:%S"`] start tar $TARDIR " >> $LOGFILE
#tar cvzf $TARNAME $THISBACKUP
#if [ $? == 0 ];then
#        echo "[`date +"%Y-%m-%d %H:%M:%S"`] end tar $TARDIR successfull" >> $LOGFILE
#else
#        echo "[`date +"%Y-%m-%d %H:%M:%S"`] end tar $TARDIR  fail" >> $LOGFILE
#        exit
#fi
#
#rm -rf $THISBACKUP
#
##################gpg files ###################################
#echo "[`date +"%Y-%m-%d %H:%M:%S"`] start  gpg $TARNAME " >> $LOGFILE
#/usr/bin/gpg -e -r chenming $TARNAME
#if [ $? == 0 ];then
#        echo "[`date +"%Y-%m-%d %H:%M:%S"`] end gpg $TARNAME successfull" >> $LOGFILE
#else
#        echo "[`date +"%Y-%m-%d %H:%M:%S"`] end gpg $TARNAME fail" >> $LOGFILE
#        exit
#fi
#
#rm -f $TARNAME
#
#echo "[`date +"%Y-%m-%d %H:%M:%S"`] start  md5sum $TARNAME.gpg " >> $LOGFILE
#md5sum $TARNAME.gpg > $TARNAME.gpg.md5
#if [ $? == 0 ];then
#        echo "[`date +"%Y-%m-%d %H:%M:%S"`] end md5sum  $TARNAME.gpg  successfull" >> $LOGFILE
#else
#        echo "[`date +"%Y-%m-%d %H:%M:%S"`] end md5sum  $TARNAME.gpg  fail" >> $LOGFILE
#        exit
#fi
#
###############transmit file #################################
#echo "[`date +"%Y-%m-%d %H:%M:%S"`] start  transmit $TARNAME.gpg "  >> $LOGFILE
#/usr/bin/scp $TARNAME.gpg $TARNAME.gpg.md5  $REMOTEBACKDIR 
#if [ $? == 0 ];then
#        echo "[`date +"%Y-%m-%d %H:%M:%S"`] end transmit $TARNAME.gpg  successfull" >> $LOGFILE
#else
#        echo "[`date +"%Y-%m-%d %H:%M:%S"`] end transmit $TARNAME.gpg  fail" >> $LOGFILE
#        exit
#fi
#
#echo "[`date +"%Y-%m-%d %H:%M:%S"`] innobackupex backup successfull "  >> $LOGFILE
#
