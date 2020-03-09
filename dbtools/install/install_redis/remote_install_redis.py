#!/usr/bin/env python
# -*- coding:utf-8 -*-

#Created by : liqingbin
#Date       : 03-05-16

import getopt
import sys
import os 
import shutil
import paramiko
import socket

######定义变量
config = {  
	"TYPE":"install",
	"DBPWD":"",
	"DBPORT":"6340",
	"DBMEMG":"1",
	"MASTER":"",
	"SLAVE":"",
	"FLAG":"0"
}  


def usage():
	print ' Redis 安装脚本使用说明'
	print ' Usage:'+sys.argv[0]+' [OPTION] [str]'
	print '	-h , --help	help'
	print '	-t , --type	install or uninstall, default install'
	print '	-p , --password	redis password ,default ""'
	print '	-P , --port	redis DBPORT ,default 6379'
	print '	-M , --memory	内存大小，单位g default 1'
	print '	-m , --master   redis master'
	print '	-s , --slave    redis slave '
	print '	-f , --flag     不安装数据库只做主从复制配置'
	sys.exit(1)

try:
	opts, args = getopt.getopt(sys.argv[1:], 'ht:p:P:M:m:s:f',
		[
			'help',
			'type=',
			'password=',
			'port=',
			'memeory=',
			'master=',
			'slave=',
			'flag'	
		])
except getopt.GetoptError, err:
	print str(err)
	usage()
	sys.exit(1)	 


for option,value in opts:
	if option in ["-h","--help"]:
		usage()
	elif option in ['-t','--type']:
		config["TYPE"]=value
	elif option in ['-p','--password']:
		config["DBPWD"]=value
	elif option in ['-P','--port']:
		config["DBPORT"]=value
	elif option in ['-M','--memory']:
		config["DBMEMG"]=value
	elif option in ['-m','--master']:
		config["MASTER"]=value
	elif option in ['-s','--slave']:
		config["SLAVE"]=value
	elif option in ['-f','--flag']:
		config["FLAG"]=1
	else:
		print 'unhandled option'
		usage()



#print config["TYPE"]

#print config["DBPWD"]
#print config["DBPORT"]
#print config["DBMEMG"]
#print config["MASTER"]
#print config["SLAVE"]
#print config["FLAG"]

#### 对输入参数合法性判断

###校验端口是不是数字
if not  config["DBPORT"].isdigit():
	print "DBPORT is not a number"
	usage()
#####校验内存是不是数字
if config["DBMEMG"].strip() and not config["DBMEMG"].isdigit():
	print "DBMEMG is not a number"
	usage()

####判断TYPE 是不是install 或者 uninstall
if (config["TYPE"] != 'install' and config["TYPE"] != 'uninstall'):
	print " -t , --type     install or uninstall, default install"
	usage()

###解析域名函数
def getIp(domain):
	print "sss" + domain
	ADDR = socket.gethostbyname(domain)
#	ADDR = socket.getaddrinfo(domain,'http')[0][4][0]
	return ADDR



###把域名解析成ip
if config["MASTER"].strip():
	config["MASTER"]=getIp(config["MASTER"])

#if config["SLAVE"].strip():
	#config["SLAVE"]=getIp(config["SLAVE"])
#	print getIp(config["SLAVE"])

TEMIP=[]
for I in config["SLAVE"].strip().split():
	I=getIp(I)
	TEMIP.append(I)
config["SLAVE"]=TEMIP



#print config["MASTER"]
print config["SLAVE"]
