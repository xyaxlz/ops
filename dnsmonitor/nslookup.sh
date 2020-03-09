#!/bin/bash

md5sum=`/usr/bin/dig +noall +answer  $1 @10.120.0.2 |grep  -o '[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}'|sort  -n |/usr/bin/md5sum|awk '{print $1}'`
echo $md5sum
echo "############################"      >> /dev/shm/$1
echo `date +["%Y-%m-%d %H:%M"]`          >> /dev/shm/$1
#/usr/bin/dig  $1                         >>  /dev/shm/$1
/usr/bin/nslookup  $1                         >>  /dev/shm/$1
echo   ""                                >>  /dev/shm/$1
#/usr/bin/dig  $1 @10.120.0.2             >>  /dev/shm/$1
/usr/bin/nslookup  $1 10.120.0.2             >>  /dev/shm/$1

#md5sum=`/usr/bin/dig +noall +answer  $1|grep  -o '[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}'|sort  -n |/usr/bin/md5sum|awk '{print $1}'`
#md5sum=`/usr/bin/dig +noall +answer  $1|sort  -n |/usr/bin/md5sum|awk '{print $1}'`
echo "" >> /dev/shm/$1

