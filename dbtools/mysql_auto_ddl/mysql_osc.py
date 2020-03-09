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
			sql='insert into cmdb.mysql_auto_ddl (hostname,port,db_name,tb_name,u_sql,add_time,start_time,end_time,exec_time,remain_time,exec_status,extra_info,exec_pct) values("%s",%d,"%s","%s","%s","%s","%s","%s",%d,%d,%d,"%s",%d) '%(hostname,int(port),db_name,tb_name,u_sql,add_time,s_time,e_time,int(exec_time),int(remain_time),int(e_status),extra_info,int(exec_pct))
			my_conn.query(sql)
		else:
			sql='update cmdb.mysql_auto_ddl set start_time="%s",end_time="%s",exec_time=%d,remain_time=%d,exec_status=%d,extra_info="%s",exec_pct=%d where hostname="%s" and port=%d and db_name="%s" and tb_name="%s" and u_sql="%s" and add_time="%s"'%(s_time,e_time,int(exec_time),int(remain_time),int(e_status),extra_info,int(exec_pct),hostname,int(port),db_name,tb_name,u_sql,add_time)
			print sql
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
        parse.add_argument('--addtime', '-a', help='add time')
        parse.add_argument('--sharding-tables-mod', action='store_true', help='DDL sharding tables model')
        parse.add_argument('--count', '-c', type=int, help='sharding tables count')
        parse.add_argument('--table-prefix', help='DDL sharding table prefix, EX. table_test_')
        parse.add_argument('--suffix-mod', type=int, default=1, help='suffix mod, 1 for decimal, 2 for hexadecimal')
        parse.add_argument('--suffix-offset', type=int, default=0, help='suffix offset, default 0')
        parse.add_argument('--non-zerofill', action='store_true', help='table suffix without zero filled')
        parse.add_argument('--alter', required=True, help='DDL sql, EX. \'add column name1 varchar(10) not null default ""\'')
        parse.add_argument('--max-lag', type=int, default=5, help='allowed all replicas\' max lag, default 5s')
        parse.add_argument('--max-load', default='Threads_running=200', help='allowed max Threads_running, default 200')
        parse.add_argument('--critical-load', default='Threads_running=500', help='abord if the load is too high, default 500')
        parse.add_argument('--no-drop-old-table', action='store_true', help='drop old table after DDL')
        parse.add_argument('--no-check-alter', action='store_true', help='check alter to warn of possible unintended behavior')
        parse.add_argument('--no-check-replication-filters', action='store_true', help='abort replication filter check')
        parse.add_argument('--dry-run', action='store_true', help='to test what will be execute')
        options = parse.parse_args()
        if options.sharding_tables_mod:
            if not options.count:
                parse.error('argument --count/-c is required when sharding-tables-mod is True')
            if not options.table_prefix:
                parse.error('argument --table-prefix is required when sharding-tables-mod is True')
        else:
            if not options.table:
                parse.error('argument --table/-t is required when sharding-tables-mod is False')
        return parse, options
    except Exception, e:
        print e

def exec_cmd(cmd,hostname,port,db_name,tb_name,sql,add_time):
    try:
	print cmd
        pipe = subprocess.Popen(cmd, stdout=subprocess.PIPE,stderr=subprocess.STDOUT,  shell=True)
	error_info=""
	e_status=0
	e_info='Prepare'
	s_time=get_time()
	e_time=''
	exec_time=0
	remain_time=0
	exec_pct=0
	FMT = '%Y-%m-%d %H:%M:%S'
	autoddl_status(hostname,port,db_name,tb_name,sql,add_time,s_time,e_time,exec_time,remain_time,e_status,e_info,exec_pct)
	time.sleep(2)
        while pipe.poll() == None:
	    line=pipe.stdout.readline()
	    exec_time=2
	    autoddl_status(hostname,port,db_name,tb_name,sql,add_time,s_time,e_time,exec_time,remain_time,e_status,e_info,exec_pct)
	    #print "Line:",line
	    if line:
		    if re.match(r'.*remain',line):
	    	    	t_line=line.split()
			exec_pct=t_line[2].split('%')[0]
			cur_time=get_time()
			exec_time=(datetime.strptime(cur_time, FMT) - datetime.strptime(s_time, FMT)).seconds
			remain_time=hour_to_second(t_line[3])
			e_status=1
			e_info='SQL Is Executing'
	    		autoddl_status(hostname,port,db_name,tb_name,sql,add_time,s_time,e_time,exec_time,remain_time,e_status,e_info,exec_pct)
		    log_rt=line.strip()
		    log(log_rt)
	    	    line=str(line).split()
	    	    if len(line)>1 and line[0]=='Error':
	    	    	error_info=log_rt
        if pipe.returncode != 0:
		err_info=pipe.stdout.readlines()
		if len(err_info)>0:
			for i in err_info:
				if re.match(r'.*Error.*',i):
					
					error_info=i.split('[')[0]
		else:
			error_info="Execute Failure"
		e_status=2
		cur_time=get_time()
		exec_time=(datetime.strptime(cur_time, FMT) - datetime.strptime(s_time, FMT)).seconds
	        e_info=error_info
	        autoddl_status(hostname,port,db_name,tb_name,sql,add_time,s_time,e_time,exec_time,remain_time,e_status,e_info,exec_pct)
                return {'status': -1, 'result': error_info}
            #raise Exception, 'exec error, returncode: %s, stderr: %s' % (pipe.returncode, pipe.stdout.readlines())
	exec_pct=100
	e_info="SQL Execute Success"
	e_time=get_time()
	remain_time=0
	e_status=3
	cur_time=get_time()
	exec_time=(datetime.strptime(cur_time, FMT) - datetime.strptime(s_time, FMT)).seconds
	autoddl_status(hostname,port,db_name,tb_name,sql,add_time,s_time,e_time,exec_time,remain_time,e_status,e_info,exec_pct)
        return {'status': 0, 'result': 'execute success'}
    except Exception, e:
	print traceback.print_exc()
        raise e

def show_create_table(host, port, user, passwd, db, table):
    try:
        connection = MySQLdb.connect(host=host, port=port, user=user, passwd=passwd, db=db, connect_timeout=3)
        cursor = connection.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        cursor.execute('set autocommit=1;')
        sql = 'show create table %s' % table
        cursor.execute(sql)
        rows = cursor.fetchall()
        cursor.close()
        connection.close()
        return {'status': 0, 'result': rows[0]}
    except Exception, e:
        return {'status': -1, 'result': 'show create table %s failed for %s' % (table, str(e))}

# change decimal to hexadecimal without 0x
def dec2hex(dec):
    return hex(dec).replace('0x', '')

# generate table suffix list
def generate_suffixs(count, suffix_mod=1, suffix_offset=0, non_zerofill=False):
    try:
        count = int(count)
        dec_len = len('%d' % (count-1))
        hex_len = len('%s' % dec2hex(count-1))
        if not non_zerofill:
            if suffix_mod == 2:
                return [('%s' % dec2hex(i+suffix_offset)).zfill(hex_len) for i in range(count)]
            return [('%d' % (i+suffix_offset)).zfill(dec_len) for i in range(count)]
        else:
            if suffix_mod == 2:
                return [('%s' % dec2hex(i+suffix_offset)) for i in range(count)]
            return [('%d' % (i+suffix_offset)) for i in range(count)]
    except Exception, e:
        raise e

# generate sharding table name list
def generate_table_names(table_prefix, count, suffix_mod=1, suffix_offset=0, non_zerofill=False):
    try:
        suffix_list = generate_suffixs(count, suffix_mod, suffix_offset, non_zerofill)
        return [table_prefix+suffix for suffix in suffix_list]
    except Exception, e:
        raise e

def osc_run(params):
    try:
        tmp_params = copy.copy(params)
	if not tmp_params['add_time']:
		add_time=get_time()
	else:
		add_time=tmp_params['add_time']
        tmp_params['password'] = ''
        log('params of mysql osc %s' % tmp_params)
        table_list = []
        if params['sharding-tables-mod']:
            table_list = generate_table_names(params['table-prefix'], params['count'], params['suffix-mod'], params['suffix-offset'], params['non-zerofill'])
        else:
            table_list.append(params['table'])
        for table in table_list:
            cmd_list = []
            cmd_list.append('/usr/bin/pt-online-schema-change')
            cmd_list.append('--host=%s --port=%d' % (params['host'], params['port']))
            cmd_list.append('--user=%s --password=%s' % (params['user'], params['password']))
            cmd_list.append('D=%s,t=%s' % (params['database'], table))
	    print "ALTER",params['alter']
            cmd_list.append('--alter="%s"' % (params['alter']))
            cmd_list.append('--max-lag=%s --max-load=%s --critical-load=%s' % (params['max-lag'], params['max-load'], params['critical-load']))
            cmd_list.append('--no-drop-old-table' if params['no-drop-old-table'] else '--drop-old-table')
            cmd_list.append('--no-check-alter' if params['no-check-alter'] else '--check-alter')
            cmd_list.append('--no-check-replication-filters' if params['no-check-replication-filters'] else '--nocheck-replication-filters')
            cmd_list.append('--dry-run' if params['dry-run'] else '--execute')
            cmd_list.append('--progress=time,5')
            cmd_list.append('--recursion-method=processlist,hosts')
            cmd_list.append('--print')
            cmd = ' '.join(cmd_list)
            ret = exec_cmd(cmd,params['host'], params['port'],params['database'], table,params['alter'],add_time)
            #if ret['status'] == 0:
            #    show_ret = show_create_table(params['host'], params['port'], params['user'], params['password'], params['database'], table)
            #    print {'status': 0, 'result': {'result': ret['result'], 'show_create_table': show_ret['result']}}
	    print "RET",ret
            time.sleep(1)
    except Exception, e:
	print traceback.print_exc()
        log('execute failed for %s' % str(e), level='error') 

def main():
    parse, opts = arg_parse()
    params = {'add_time':opts.addtime,'host': opts.host, 'port': opts.port, 'user': opts.user, 'password': opts.password, 
              'database': opts.database, 'table': opts.table, 'alter': opts.alter, 'max-lag': opts.max_lag, 
              'max-load': opts.max_load, 'critical-load': opts.critical_load, 'dry-run': opts.dry_run, 
              'no-drop-old-table': opts.no_drop_old_table, 'no-check-alter': opts.no_check_alter,
              'no-check-replication-filters': opts.no_check_replication_filters,
              'sharding-tables-mod': opts.sharding_tables_mod, 'count': opts.count, 'table-prefix': opts.table_prefix,
              'suffix-mod': opts.suffix_mod, 'suffix-offset': opts.suffix_offset, 'non-zerofill': opts.non_zerofill}
    osc_run(params)

if __name__ == '__main__':
    main()
