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
#from config_set  import *
from mysql_lib import *


from warnings import filterwarnings
filterwarnings('ignore', category = MySQLdb.Warning)

#global variables
db_black_list = ["mysql","performance_schema","zjmdmm","information_schema",\
                 "nagiosdmm","xddmm","tcdmm",]
mysql_user='db_admin'
mysql_passwd=''
VERSION='1.0'
center_host='192.168.7.29'
source_dir='source_pack'
dest_dir='/tmp'
rsync_mod='data'
db_user='mysql'
db_group='mysql'
##################################
LOG_PREFIX = "/tmp/"
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
    return parse, parse.parse_args()


###################################
##main
#if __name__ == '__main__':

def main():
   try:
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
	    host='127.0.0.1'
	    conn=get_conn(user=mysql_user,passwd=mysql_passwd,host=host,port=db_port)
	    conn=conn['value']
	    rt={} 
	    if not conn:
		   rt['status']=-1
		   rt['info']='Error:get connection Failed'
		   return rt
	    sql="show global variables like '%slow_query_log_file%';"
	    sql_rt=exec_sql(conn,sql)
	    if sql_rt['status']!=0:
		return  sql_rt
	    sql_rt=sql_rt['result']
	    slow_log_file=sql_rt[0]['Value']
	    get_ip_cmd="/sbin/ifconfig |grep inet|cut -f2 -d:|cut -f1 -d ' '|sort -nr|head -n 1"
	    ip_addr=run_command(get_ip_cmd)[0].strip()
	    if len(ip_addr)==0:
		    rt['status']=-1
		    rt['info']='Get IP failed'
		    return rt
	    pt_query_cmd='pt-query-digest --user=anemometer --password=g5BjftQPZfN9m6MJ --review h=192.168.7.29,P=10001,D=slow_query_log,t=global_query_review --history h=192.168.7.29,P=10001,D=slow_query_log,t=global_query_review_history  --log=/tmp/pt-query-digest.log  --daemonize --no-report --limit=0%% --filter="\$event->{Bytes} = length(\$event->{arg}) and \$event->{hostname}=\'%s\' and \$event->{dbport}=%s"  %s' % (str(ip_addr),str(db_port),str(slow_log_file))
	    query_rt=run_command(pt_query_cmd)[0]
	    if not query_rt:
		rt['status']=0
		rt['result']='slow query log digest success'
	    else:
		rt['status']=-1
		rt['result']='slow query log digest failed'
	    return rt
   except Exception,e:
	print traceback.print_exc()    
	
print main()
