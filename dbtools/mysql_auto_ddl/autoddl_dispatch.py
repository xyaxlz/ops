#! /usr/bin/python2.7
# encoding=utf-8
__author__ = 'zolker'

'''
Package pt online schema change for simple use.
'''

import os
import sys
import argparse
import MySQLdb
import subprocess
import time
from datetime import datetime
import logging
import traceback
import copy
from warnings import filterwarnings
filterwarnings('ignore', category = MySQLdb.Warning)
sys.path.append('/etc/db_tools')
from mysqllib import *
from syslib import *
reload(sys)
sys.setdefaultencoding('utf-8')

db_user = 'superdba'
db_passwd = '5CHcQzFhIbVaTHzL'
admin_user='db_admin'
admin_passwd='BZs*gIyVeH4o0q!f'
admin_port=3307
admin_host='127.0.0.1'

# print to screen
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

log_map = {}

def get_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
def hour_to_second(t):
	return sum(int(x) * 60 ** i for i,x in enumerate(reversed(t.split(":"))))

def log(log_msg, level='debug', filename='mysql_osc'):
    try:
        if filename in log_map:
            tmp_log=log_map.get(filename)
        else:
            tmp_log=logging.getLogger(filename)
            tmp_log.setLevel(logging.DEBUG)
            tmp_formatter = logging.Formatter(" %(asctime)s - %(message)s")
            log_base_dir = '/www/db_tools_logs/'
            if not os.path.exists(log_base_dir):
                os.makedirs(log_base_dir)
            tmp_handler = logging.FileHandler(log_base_dir + filename + ".log")
            tmp_handler.setFormatter(tmp_formatter)
            tmp_log.addHandler(tmp_handler)
            log_map[filename]=tmp_log
        if level!='debug':
            tmp_log.debug(log_msg, exc_info=True)
        else:
            tmp_log.debug(log_msg)
    except Exception, e:
        print e

def autoddl_status(hostname,port,db_name,tb_name,u_sql,add_time,s_time,e_time,exec_time,remain_time,e_status,extra_info,exec_pct):
	try:
		my_conn=MySQLBase(admin_host,admin_port,admin_user,admin_passwd)
		if int(exec_time)==0:
			sql="insert into cmdb.mysql_auto_ddl (hostname,port,db_name,tb_name,u_sql,add_time,start_time,end_time,exec_time,remain_time,exec_status,extra_info,exec_pct) values('%s',%d,'%s','%s','%s','%s','%s','%s',%d,%d,%d,'%s',%d) "%(hostname,int(port),db_name,tb_name,u_sql,add_time,s_time,e_time,int(exec_time),int(remain_time),int(e_status),extra_info,int(exec_pct))
			my_conn.query(sql)
		else:
			sql="""update cmdb.mysql_auto_ddl set start_time='%s',end_time='%s',exec_time=%d,remain_time=%d,exec_status=%d,extra_info="%s",exec_pct=%d where hostname='%s' and port=%d and db_name='%s' and tb_name='%s' and u_sql='%s' and add_time='%s'"""%(s_time,e_time,int(exec_time),int(remain_time),int(e_status),extra_info,int(exec_pct),hostname,int(port),db_name,tb_name,u_sql,add_time)
			my_conn.query(sql)
	except Exception ,e:
		print traceback.print_exc()

def arg_parse():
    try:
        parse = argparse.ArgumentParser(description='Mysql online schema change') 
        parse.add_argument('--host', '-H', required=True, help='mysql host')
        parse.add_argument('--port', '-P', type=int, required=True, help='mysql port')
        parse.add_argument('--user', '-u', default=db_user, help='mysql user, default superdba')
        parse.add_argument('--password', '-p', default=db_passwd, help='mysql user password')
        parse.add_argument('--database', '-D', required=True, help='DDL database')
        parse.add_argument('--table', '-t', help='DDL table')
        parse.add_argument('--sql', '-S', help='SQL')
	options = parse.parse_args()
        return parse, options
    except Exception, e:
        print e

def find_next_task():
	try:
		my_conn=MySQLBase(admin_host,admin_port,admin_user,admin_passwd)	
		sql="select hostname,port,db_name,tb_name,u_sql,add_time  from cmdb.mysql_auto_ddl where exec_status=0 order by id limit 1;"
		sql_rt=my_conn.query(sql)
		return sql_rt
        except Exception, e:
        	print e

def find_exec_task():
	try:
		my_conn=MySQLBase(admin_host,admin_port,admin_user,admin_passwd)	
		sql="select hostname,port,db_name,tb_name,u_sql,add_time  from cmdb.mysql_auto_ddl where exec_status=1;"
		sql_rt=my_conn.query(sql)
		return sql_rt
        except Exception, e:
        	print e
def cmd_run(cmd):
	try:
		pipe=subprocess.Popen(cmd, stdout=subprocess.PIPE,stderr=subprocess.STDOUT,  shell=True)
		stdout,stderr = pipe.communicate()
		print "OUT",stdout
		print "Err",stderr
                return_code=pipe.returncode
		return return_code
        except Exception, e:
        	print e
	

def main():
	while True:
		exec_rt=find_exec_task()
		#print "EXEC:",exec_rt
		if len(exec_rt)==0:
			next_rt=find_next_task()
			if len(next_rt)==0:
				time.sleep(10)
				continue
			next_rt=next_rt[0]
			port=next_rt['port']
			host=next_rt['hostname']
			db_name=next_rt['db_name']
			tb_name=next_rt['tb_name']
			u_sql=next_rt['u_sql']
			print u_sql
			add_time=next_rt['add_time']
			cmd='python2.7 /home/yangshanggang/proj/mysql_osc.py -P %d -H %s -D %s -t %s  -a "%s" --alter "%s"'%(int(port),host,db_name,tb_name,add_time,u_sql)
			print cmd
			print cmd_run(cmd)
			time.sleep(5)
			
		else:
			time.sleep(10)
if __name__ == '__main__':
    main()
