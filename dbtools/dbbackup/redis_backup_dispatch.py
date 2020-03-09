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
import redis
import copy
from daemon import Daemon
from warnings import filterwarnings
filterwarnings('ignore', category = MySQLdb.Warning)
sys.path.append('/etc/db_tools')
from mysqllib import *
import mysqllib
from syslib import *
reload(sys)
sys.setdefaultencoding('utf-8')

db_user = 'superdba'
db_passwd = '5CHcQzFhIbVaTHzL'
admin_user='db_admin'
admin_passwd='BZs*gIyVeH4o0q!f'
admin_port=3307
admin_host='127.0.0.1'

metadb_user = 'superdba'
metadb_passwd = '5CHcQzFhIbVaTHzL'
metadb_host = '10.110.17.6'
metadb_port = 3307
backup_user = 'db_admin'
backup_passwd = 'BZs*gIyVeH4o0q!f'
metadb_dbname = 'cmdb'

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
    return time.strftime("%Y%m%d", time.localtime())
def get_hour():
    return time.strftime("%H:%M:%S", time.localtime())
def hour_to_second(t):
	return sum(int(x) * 60 ** i for i,x in enumerate(reversed(t.split(":"))))

def log(log_msg, level='debug', filename='redis_backup'):
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
		sql="select ip as host,a.port,backup_type  from cmdb.redis_backup_policy as  a left join cmdb.redis_ins as b on a.port=b.port  where b.db_role=0 ;"
		sql_rt=my_conn.query(sql)
		return sql_rt
        except Exception, e:
        	print e
def check_comp_task(host,port):
	try:
		my_conn=MySQLBase(admin_host,admin_port,admin_user,admin_passwd)	
		cur_day=get_day()
		sql=" select count(*) as ct from cmdb.redis_backup_status where host='%s' and port=%d and backup_status in (0,2) and start_time>'%s'"%(host,port,cur_day)
		sql_rt=my_conn.query(sql)
		success_ct=sql_rt[0]['ct']
		sql=" select count(*) as ct from cmdb.redis_backup_status where host='%s' and port=%d and start_time>'%s'"%(host,port,cur_day)
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

def dblog(dblog_msg, dblog_status):
    try:
        if dblog_status is False:
            return
        #dblog_msg['extra_info'] = mysqllib.escape_string(dblog_msg['extra_info'])
        cond_list = ["%s='%s'" % (k, v) for k, v in dblog_msg.items()]
        sql = '''replace into cmdb.redis_backup_status set %s;''' % ','.join(cond_list)
	print sql
        mysqlbase = mysqllib.MySQLBase(metadb_host, metadb_port, backup_user, backup_passwd, db=metadb_dbname)
        mysqlbase.query(sql, fetch=False)
    except Exception, e:
        log('dblog failed for %s' % str(e), level='error')
	

def schedule():
	while True:
		try:
			dblog_status=True
			cur_hour=get_hour()
			while (cur_hour<'05:20:00' or cur_hour>'10:00:00'):
				time.sleep(600)
				cur_hour=get_hour()
			exec_rt=find_all_task()
		#	print exec_rt
		#	sys.exit()
			#exec_rt=({'host': u'10.110.16.52', 'port': 6379},)	
			for i in exec_rt:
				print i 
				check_rt=check_comp_task(i['host'],i['port'])
				print check_rt
				if not check_rt:
					dest_dir="/data/dbbackup/redis/%s/%s"%(str(i['port']),get_day())
					if not os.path.exists(dest_dir):
						os.makedirs(dest_dir)
					start_time=get_time()
					dblog_msg={"host":i['host'],"port":i['port'],"start_time":start_time,"end_time":'',"backup_size":0,"backup_status":2}
				        dblog(dblog_msg,dblog_status)	
					if i['backup_type']==0:
						backup_file="redis_%s.rdb"%(str(i['port']))
					elif i['backup_type']==1:
						backup_file="append_%s.aof"%(str(i['port']))
					cmd='scp -r -l 200000 %s:/data/redis/%s/data/%s %s'%(i['host'],str(i['port']),backup_file,dest_dir)
					print cmd
					bk_rt=cmd_exec(cmd)
					end_time=get_time()
					back_size=os.path.getsize('%s/redis_%s.rdb'%(dest_dir,str(i['port'])))
					backup_size=int(back_size/1024/1024)
					if bk_rt['status']==0 and back_size>0:
						backup_status=0
					else:
						backup_status=1
					dblog_msg={"host":i['host'],"port":i['port'],"start_time":start_time,"end_time":end_time,"backup_size":backup_size,"backup_status":backup_status}
				        dblog(dblog_msg,dblog_status)	
					time.sleep(60)
		        time.sleep(3600)
			
		except Exception,e:
			print e
class MyDaemon(Daemon):
    def run(self):
        schedule()
			
def main():
    parse, opts = arg_parse()
    if opts.daemonize is True:
        pid_file = '/tmp/redis_backup_schedule.pid'
        mydaemon = MyDaemon(pid_file, verbose=0)
        print 'redis backup scheduler starting...  pid file: %s' % pid_file
        mydaemon.start()
    else:
        schedule()
if __name__ == '__main__':
    #print hour_to_second('03:03:03')	
    #sys.exit()
    main()
    

