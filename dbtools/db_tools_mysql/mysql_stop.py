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
mysql_user='db_admin'
mysql_passwd='BZs*gIyVeH4o0q!f'
VERSION='1.0'
center_host='10.110.17.6'
source_dir='db'
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
    parse.add_argument('--port', '-P', type=int, required=True,
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
	
    #check_pid='ps aux|grep mysql|grep %s|grep -v grep|wc -l'%(str(db_port))
    if  os.path.exists(db_data_dir): 
	check_pid='ps aux|grep mysql|grep %s|grep -v grep|grep -v python|wc -l'%(str(db_port))
	check_pid_rt=run_command(check_pid)[0]
	if int(check_pid_rt)==0:
            rt['status']=-1
            rt['info']='Check MySQL Pid Failed!'
            return rt
        socket_path='/tmp/my%s.sock'%(str(db_port))
	if  not os.path.exists(socket_path):
	       get_socket_path_cmd="ps aux|grep mysql|grep %s|grep socket|grep -v grep|grep -v python"%(str(db_port))
	       socket_path_rt=run_command(get_socket_path_cmd)[0]
	       socket_path_rt=socket_path_rt.split()
	       pt=re.compile(r'.*socket.*')
	       for i in socket_path_rt:
	           if  pt.search(i):
			socket_path=i.split('=')[1]
	       if len(socket_path_rt)==0:
			rt['status']=-1
			rt['info']='Get Socket Path Failed!'
			return rt

	shutdown_cmd="mysqladmin -u%s -p%s -S %s  shutdown &"%(mysql_user,mysql_passwd,socket_path)
	start_rt=run_command(shutdown_cmd)
	rt['status']=0
	rt['info']='Stop MySQL Success!'

	return rt


    else:
	rt['status']=-1
	rt['info']='datadir is not exists'
	return rt
print main()
