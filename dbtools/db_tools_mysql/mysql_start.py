#! /usr/bin/python2.7

#Created zolker



import argparse
import sys
import os
import stat
import socket
import time
import threading
import re
import logging
import copy
import MySQLdb
import subprocess 
from config_set  import *


from warnings import filterwarnings
filterwarnings('ignore', category = MySQLdb.Warning)

#global variables
db_black_list = ["mysql","performance_schema","zjmdmm","information_schema",\
                 "nagiosdmm","xddmm","tcdmm",]
mysql_user='root'
mysql_passwd=''
VERSION='1.0'
center_host='10.110.17.6'
source_dir='source_pack'
dest_dir='/tmp'
rsync_mod='data'
db_user='mysql'
db_group='mysql'
##################################
LOG_PREFIX = "/tmp/"
mysql_bin_prefix="/usr/local"
logger_s = None #log for program internal
logger_u = None #log for user
##################################

#config = NewRawConfigParser(allow_no_value=True,new_option_len=33)
#config.read("a.cnf")
#print config.get("mysqld","user")
#config.set("mysqld","user","xinyu7")
#print config.get("mysqld","user")
#with open("a.cnf",'wb') as configfile:
#    config.write(configfile)



def run_command(command):
    p = subprocess.Popen(command, shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
    return p.communicate()


def getLogger(user_log, log_level):
    system_log = "/tmp/mysql-login_YnzAtZxuldXq.log"
    if user_log and user_log.startswith("/"):
        log_dest = user_log
    elif user_log:
        log_dest = LOG_PREFIX + user_log
    else:
        log_dest = None
    logger_s = logging.getLogger("intertal-"+str(VERSION))
    logger_s.setLevel(logging.DEBUG)

    logger_u = logging.getLogger("user-"+str(VERSION))
    logger_u.setLevel(log_level)

    #if path is a dir, exit the program
    if log_dest and os.path.isdir(log_dest):
        print "system log destination(%s) is a dir, not a file!" % log_dest
        sys.exit(-1)
    if log_dest and os.path.isdir(system_log):
        print "user log destination(%s) is a dir, not a file!" % system_log 
        sys.exit(-1)
    #if file not exists, touch it  and it's permisson to 777
    if log_dest and not os.path.exists(log_dest):
        os.mknod(log_dest)
        os.chmod(log_dest, stat.S_IRWXU+stat.S_IRWXG+stat.S_IRWXO)
    if log_dest and not os.path.exists(system_log):
        os.mknod(system_log)
        os.chmod(system_log, stat.S_IRWXU+stat.S_IRWXG+stat.S_IRWXO)
    if not log_dest:
        file_handler_u = logging.StreamHandler(sys.stdout)
    else:
        file_handler_u = logging.FileHandler(log_dest)
    print "System log redirect to %s" % system_log
    print "User log redirect to %s" % (log_dest if log_dest else "STDOUT")
    print ""
    file_handler_s = logging.FileHandler(system_log)
    
    formatter_s = logging.Formatter("%(asctime)s - [%(levelname)s] - "+
           "[%(name)s/%(filename)s: %(lineno)d] - %(message)s")
    formatter_u = logging.Formatter("%(message)s")
    file_handler_s.setFormatter(formatter_s)
    file_handler_u.setFormatter(formatter_u)
    logger_s.addHandler(file_handler_s)
    logger_u.addHandler(file_handler_u)
    return logger_s, logger_u



def arg_parse():

    parse = argparse.ArgumentParser(description='Install  MySQL')
    parse.add_argument('--port', '-P', type=int, default=3306,
                       help='mysql port')
    parse.add_argument('--version', '-v', default='5.6.28',
                       help='mysql version')
    parse.add_argument('--datadir', '-d', default='data',help='mysql datadir')
    return parse, parse.parse_args()


###################################

def main():
    parser, opts = arg_parse()
    args_len=len(sys.argv)
    # Debug it or not
    try:
        MYSQLSAR_DEBUG = os.environ['MYSQLSAR_DEBUG']
    except KeyError, err:
        MYSQLSAR_DEBUG = False

    if MYSQLSAR_DEBUG:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO 

    # The argparse module isn't perfect, we do some option confict check.
    db_port=opts.port
    db_version=opts.version
    datadir='/%s'%opts.datadir
    db_data_dir='%s/mysql%s'%(datadir,str(db_port))
    config_path='%s/mysql%s/my%s.cnf'%(datadir,str(db_port),str(db_port))
    rt={}
    if  os.path.exists(db_data_dir): 
	chown_datadir_cmd='chown -R %s.%s %s'%(db_user,db_group,db_data_dir)
	chown_datadir_rt=run_command(chown_datadir_cmd)
	db_version_cmd="cat %s|grep MySQL_Version|cut -f3 -d' '"%(config_path)
       	db_version_rt=run_command(db_version_cmd)[0]
	if len(db_version_rt)==0 or db_version_rt==None:
            rt['status']=-1
            rt['info']='Get MySQL Version Failed!'
            return rt
	db_version_rt=db_version_rt.strip()
	post_mysql_bin='%s/%s'%(mysql_bin_prefix,db_version_rt)
	if not os.path.exists(post_mysql_bin):
            rt['status']=-1
            rt['info']='mv mysql bin  failed'
            return rt
	start_cmd="cd %s;./bin/mysqld_safe --defaults-file=%s > /dev/null 2>&1 &"%(post_mysql_bin,config_path)
	start_rt=run_command(start_cmd)[0]
	if len(start_rt)==0:
		rt['status']=0
		rt['info']='Start MySQL Success!'
	else:
		rt['status']=-1
		rt['info']='Start MySQL Failed!'

	return rt
    else:
	rt['status']=-1
	rt['info']='datadir is not exists'
	return rt
print main()
