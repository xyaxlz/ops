#!/usr/bin/env python
# -*- coding:utf-8 -*-

#Created by : liqingbin
#Date       : 03-05-16

import getopt
import sys
import os 
import shutil

####设置默认参数
config = {  
	"TYPE":"install",  
	"DBPWD":"",        
	"DBPORT":"6340",      
	"DBMEMG":"1"  
}  


def usage():
	print ' Redis 安装脚本使用说明'
	print ' Usage:'+sys.argv[0]+' [OPTION] [str]'
	print '	-h , --help	help'
	print '	-t , --type	install or uninstall, default install'
	print '	-p , --password	redis password ,default ""'
	print '	-P , --port	redis DBPORT ,default 6379'
	print '	-M , --memory	内存大小，单位g default 1'
	sys.exit(1)

try:
	opts, args = getopt.getopt(sys.argv[1:], 'ht:p:P:M:',
		[
			'help',
			'type=',
			'password=',
			'port=',
			'memory='
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
	else:
		print 'unhandled option'
		usage()

####校验参数的有效性

if not  config["DBPORT"].isdigit():
	print "DBPORT is not a number"
	usage()

if config["DBMEMG"].strip() and not config["DBMEMG"].isdigit():
	print "DBMEMG is not a number"
	usage()


if (config["TYPE"] != 'install' and config["TYPE"] != 'uninstall'):
	print " -t , --type     install or uninstall, default install"
	usage()


####redis安装

def install():

	if not os.path.exists("/data/redis/"+config["DBPORT"]+"/log/"):
		os.makedirs("/data/redis/"+config["DBPORT"]+"/log/") 
		
	if not os.path.exists("/data/redis/"+config["DBPORT"]+"/data/"):
		os.makedirs("/data/redis/"+config["DBPORT"]+"/data/") 
	
	if not os.path.exists("/etc/redis/"):
		os.makedirs("/etc/redis/") 
	
	shutil.copyfile("redis_init_script","/etc/init.d/redis_"+config["DBPORT"])
	shutil.copyfile("redis.conf","/etc/redis/"+config["DBPORT"]+".conf")
	shutil.copyfile("redislogin","/usr/bin/redislogin_"+config["DBPORT"])
	os.chmod("/usr/bin/redislogin_"+config["DBPORT"], 0755)
	os.system('sed -i "s/6379/'+config["DBPORT"]+'/g" /usr/bin/redislogin_'+config["DBPORT"])
	os.system('sed -i "s/6379/'+config["DBPORT"]+'/g" /etc/init.d/redis_'+config["DBPORT"])
	os.system('sed -i "s/6379/'+config["DBPORT"]+'/g" /etc/redis/'+config["DBPORT"]+'.conf')
	
	if  config["DBPWD"].strip():
		
		os.system('sed -i "/^masterauth/d"  /etc/redis/'+config["DBPORT"]+'.conf')
		os.system('sed -i "/^requirepass/d"  /etc/redis/'+config["DBPORT"]+'.conf')
		os.system('sed -i "/^#masterauth/a\masterauth '+config["DBPWD"]+'"  /etc/redis/'+config["DBPORT"]+'.conf')
		os.system('sed -i "/^#requirepass/a\\requirepass  '+config["DBPWD"]+'"  /etc/redis/'+config["DBPORT"]+'.conf')
	if config["DBMEMG"].strip():
		os.system('sed -i  "s/^maxmemory .*/maxmemory '+config["DBMEMG"]+'Gb/g" /etc/redis/'+config["DBPORT"]+'.conf')
	
	os.chmod("/etc/init.d/redis_"+config["DBPORT"], 0755)
	os.system('chkconfig  --add redis_'+config["DBPORT"])
	os.system('chkconfig redis_'+config["DBPORT"]+'  on')
	os.system('/etc/init.d/redis_'+config["DBPORT"]+' start')

def uninstall():
	
	if os.system('/etc/init.d/redis_'+config["DBPORT"]+' stop'):
		sys.exit(1)
	os.system('chkconfig  --del redis_'+config["DBPORT"])
	if config["DBPORT"].strip():
		if os.path.exists('/data/redis/'+config["DBPORT"]):
			shutil.rmtree('/data/redis/'+config["DBPORT"])
		if os.path.exists('/etc/init.d/redis_'+config["DBPORT"]):
			os.remove('/etc/init.d/redis_'+config["DBPORT"])
		if os.path.exists('/etc/redis/'+config["DBPORT"]+'.conf'):
			os.remove('/etc/redis/'+config["DBPORT"]+'.conf')
		if os.path.exists('/usr/bin/redislogin_'+config["DBPORT"]):
			os.remove('/usr/bin/redislogin_'+config["DBPORT"])

if config["TYPE"] == 'install' :
	install()
elif config["TYPE"] == 'uninstall':
	uninstall()
