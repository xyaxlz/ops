#!/bin/bash
rpm -qa|grep ops-tools > /dev/null 2>&1
[ $? -ne 0 ] && rpm -ivh ops-tools-1.0.2-1.noarch.rpm
grep 'liufeng' /etc/sudoers > /dev/null 2>&1
[ $? -ne 0 ] && echo 'liufeng	ALL=(ALL) 	ALL' >> /etc/sudoers
greo 'huanghuan' /etc/sudoers > /dev/null 2>&1
[ $? -ne 0 ] && echo 'huanghuan   ALL=(ALL)       ALL' >> /etc/sudoers
