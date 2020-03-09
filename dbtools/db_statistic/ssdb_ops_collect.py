#! /usr/bin/python2.7

#Created zolker

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
import redis
import subprocess 
import traceback
from warnings import filterwarnings
filterwarnings('ignore', category = MySQLdb.Warning)
sys.path.append('/etc/db_tools')
from mysqllib import *
from syslib import *

#global variables
db_black_list = ["mysql","performance_schema","zjmdmm","information_schema",\
                 "nagiosdmm","xddmm","tcdmm",]
admin_user='db_admin'
admin_passwd='BZs*gIyVeH4o0q!f'
admin_port=3307
admin_host='127.0.0.1'
VERSION='1.0'

##################################
LOG_PREFIX = "/tmp/"
logger_s = None #log for program internal
logger_u = None #log for user
##################################

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


class Connection:

    def __init__(self, *args, **kargs):
        self.args = args
        self.kargs = kargs
        self.kargs['user'] = kargs['user'] if kargs.has_key('user') \
                                           else opts.user
        self.kargs['passwd'] = kargs['passwd'] if kargs.has_key('passwd') \
                                               else opts.passwd
        self.kargs['connect_timeout'] = kargs['connect_timeout'] \
                                        if kargs.has_key('connect_timeout') \
                                        else 5
        # TODO: we need to overwrite other argument. 
        #      such interactive_timeout/wait_tiemout/charset and so on

    def get_connection(self,):
        ret = {'errno':0, 'errmsg':"", 'value':None}
        conn = None

        try:
            # TODO: add a connect retry mechaniam
	    #print self.kargs
            conn = MySQLdb.connect(*self.args, **self.kargs)
            ret['value'] = conn
        except Exception, err:
            ret['errno'] = 1
            ret['errmsg'] = str(err)
        finally:
            return ret

# Wrapper for MySQL connection
def get_conn(*args, **kargs):
    #must *args, **kargs, not args, kargs
    __conn__ = Connection(*args, **kargs)
    return __conn__.get_connection()

def close_connection(conn):
    ret = {'errno':0, 'msg':"close connection success", 'value':None}
    try:
        if conn:
            conn.close()
    except Exception, err:
        ret['errno'] = 1
        ret['msg'] = str(err)
    finally:
        return ret

def close_cursor(cursor):
    ret = {'errno':0, 'msg':"close cursor succuss", 'value':None}
    try:
        if cursor:
            cursor.close()
    except Exception, err:
        ret['errno'] = 1
        ret['msg'] = str(err)
    finally:
        return ret

def exec_sql(conn,sql):
	try:
		cursor=conn.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute(sql)
		sql_rt=cursor.fetchall()
		rt={}
		rt['status']=0
		rt['result']=sql_rt
		return rt
	except Exception,error:
		rt={}
		rt['status']=-1
		rt['result']='SQL exec Error'
		return rt

def get_ssdb_host():
    try:
        conn=get_conn(user=admin_user,passwd=admin_passwd,host=admin_host,port=admin_port)
        conn=conn['value']
        sql="select hostname,port  from cmdb.ssdb_ins;"
        sql_rt=exec_sql(conn,sql)
        return sql_rt
    except Exception,error:
        print traceback.print_exc()
        rt={}
        rt['status']=-1
        rt['result']='SQL exec Error'
        return rt
		
		
    
def get_slave_ip():
	return 0


#connect = Connect = get_connection


def get_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def get_hour():
    return time.strftime("%Y-%m-%d %H:00:00", time.localtime())
def get_day():
    return time.strftime("%Y-%m-%d 00:00:00", time.localtime())


def collect_ssdb_ops(hostname,port):
    try:
        r_ins=redis.StrictRedis(host=hostname,port=port,db=0,password=password)
    except Exception,e:
        print traceback.print_exc()
#print rt
def  ssdb_status():
    ssdb_host=get_ssdb_host()
    ssdb_host=ssdb_host['result']
    cur_time=get_hour()
    if len(ssdb_host)==0:
        rt={}
        rt['status']=-1
        rt['result']='Get Host Failed'
    for i in ssdb_host:
        hostname=i['hostname']
        port=i['port']
        print hostname,port
 	ssdb_cmd='/usr/local/ssdb/ssdb-cli -p  %s -h  %s info'%(str(port),hostname)
        ssdb_info=cmd_exec(ssdb_cmd)
        rt={}
        if len(ssdb_info)==0 or ssdb_info['status']==-1:
            rt['status']=-1
            rt['result']='SSDB Info Get Failed!'
	    print  rt
	    continue
        ssdb_info=ssdb_info['result']
        ssdb_info=ssdb_info.split('\n')
        for  i in ssdb_info:
        	if re.match(r'.*total_calls.*',i):
			total_ops=int(i.split(':')[-1])
        	if re.match(r'.*read_calls.*',i):
			read_ops=int(i.split(':')[-1])
        	if re.match(r'.*write_calls.*',i):
			write_ops=int(i.split(':')[-1])
        sql="replace into cmdb.ssdb_hour_ops(hostname,port,day_time,total_ops,read_ops,write_ops) values('%s',%d,'%s',%d,%d,%d)"%(hostname,int(port),cur_time,total_ops,read_ops,write_ops)
        #print redis_conn.info()
        #day_time=get_day()
        conn=get_conn(user=admin_user,passwd=admin_passwd,host=admin_host,port=admin_port)
        conn=conn['value']
        conn.autocommit(1) 
        rt_sql=exec_sql(conn,sql)

#main()
#print collect_mysql_data_size('192.168.7.27',3307)
#print collect_redis_ops('192.168.9.156')
#print get_redis_password('rdb1v.infra.bjza.pdtv.it',6084)
print ssdb_status()
