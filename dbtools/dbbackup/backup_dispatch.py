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
from daemon import Daemon
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
def get_day():
    return time.strftime("%Y-%m-%d", time.localtime())
def get_hour():
    return time.strftime("%H:%M:%S", time.localtime())
def hour_to_second(t):
	return sum(int(x) * 60 ** i for i,x in enumerate(reversed(t.split(":"))))

def log(log_msg, level='debug', filename='mysql_backup'):
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

def backup_status(host,port,backup_method,backup_period,start_time,end_time,backup_size,back_status,prepare_status,extra_info):
	try:
		my_conn=MySQLBase(admin_host,admin_port,admin_user,admin_passwd)
		if int(exec_time)==0:
			sql="insert into cmdb.db_backup_status (host,port,backup_method,backup_period,start_time,end_time,backup_size,back_status,prepare_status,extra_info) values('%s',%d,'%s','%s','%s','%s',%d,%d,%d,'%s')"%(str(host),int(port),str(backup_method),str(backup_period),str(start_time),str(end_time),int(backup_sise),int(backup_status),int(prepare_status),str(extra_info))
			my_conn.query(sql)
		else:
			sql="""update cmdb.db_backup_status  set backup_period='%s',end_time='%s',backup_size=%d,back_status=%d,prepare_status=%d,extra_info="%s" where host='%s' and port=%d and backup_method='%s' and start_time='%s'"""%(str(backup_period),end_time,int(backup_size),int(back_status),int(prepare_status),str(extra_info),host,int(port),str(backup_method),start_time)
			my_conn.query(sql)
	except Exception ,e:
		print traceback.print_exc()

def arg_parse():
    try:
        parse = argparse.ArgumentParser(description='Mysql backup schedule')
        parse.add_argument('--daemonize', '-d', action='store_true', help='running with daemonize module')
        return parse, parse.parse_args()

    except Exception, e:
        print e

def find_next_task():
	try:
		my_conn=MySQLBase(admin_host,admin_port,admin_user,admin_passwd)	
		sql="select host,port,backup_method,backup_period,keep_days  from cmdb.db_backup_policy ;"
		sql_rt=my_conn.query(sql)
		return sql_rt
        except Exception, e:
        	print e

def find_all_task():
	try:
		my_conn=MySQLBase(admin_host,admin_port,admin_user,admin_passwd)	
		sql=" select host,a.port,backup_method,backup_period,keep_days,prod_info  from cmdb.db_backup_policy as a left join cmdb.mysql_ins as b  on a.host=b.ip"
		sql_rt=my_conn.query(sql)
		return sql_rt
        except Exception, e:
        	print e
def check_comp_task(host,port):
	try:
		my_conn=MySQLBase(admin_host,admin_port,admin_user,admin_passwd)	
		cur_day=get_day()
		sql=" select count(*) as ct from cmdb.db_backup_status where host='%s' and port=%d and back_status in (0,2) and start_time>'%s'"%(host,port,cur_day)
		sql_rt=my_conn.query(sql)
		success_ct=sql_rt[0]['ct']
		sql=" select count(*) as ct from cmdb.db_backup_status where host='%s' and port=%d and start_time>'%s'"%(host,port,cur_day)
		sql_rt=my_conn.query(sql)
		fail_ct=sql_rt[0]['ct']
		if success_ct>0 or fail_ct>3:
			return True
		else:
			return False
        except Exception, e:
        	print e
def cmd_run(cmd):
	try:
		pipe=subprocess.Popen(cmd, stdout=subprocess.PIPE,stderr=subprocess.STDOUT,  shell=True)
		stdout,stderr = pipe.communicate()
                return_code=pipe.returncode
		return return_code
        except Exception, e:
        	print e
	

def schedule():
	while True:
		try:
			cur_hour=get_hour()
			while (cur_hour<'03:00:00' or cur_hour>'19:00:00'):
				time.sleep(3600)
				cur_hour=get_hour()
			exec_rt=find_all_task()
			for i in exec_rt:
				print i 
				check_rt=check_comp_task(i['host'],i['port'])
				print check_rt
				if not check_rt:
					cmd='python2.7 /etc/db_tools/mysql_backup.py -H %s -P %d -T %s'%(i['host'],i['port'],i['prod_info'])
					print cmd
					bk_rt=sys_cmd(i['host'],cmd)
					print "RT",bk_rt
					time.sleep(5)
		        time.sleep(3600)
			
		except Exception,e:
			print e
class MyDaemon(Daemon):
    def run(self):
        schedule()
			
def main():
    parse, opts = arg_parse()
    if opts.daemonize is True:
        pid_file = '/tmp/mysql_backup_schedule.pid'
        mydaemon = MyDaemon(pid_file, verbose=0)
        print 'mysql backup scheduler starting...  pid file: %s' % pid_file
        mydaemon.start()
    else:
        schedule()
if __name__ == '__main__':
    #print hour_to_second('03:03:03')	
    #sys.exit()
    main()
    

