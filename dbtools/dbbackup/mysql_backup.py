#! /usr/bin/python2.7
# encoding=utf-8
__author__ = 'zolker'

'''
Mysql backup script.
'''

import os
import re
import argparse
import subprocess
import datetime
import time
import logging
import traceback
import sys
import  mysqllib

metadb_user = 'superdba'
metadb_passwd = '5CHcQzFhIbVaTHzL'
metadb_host = '10.110.17.6'
metadb_port = 3307
backup_user = 'db_admin'
backup_passwd = 'BZs*gIyVeH4o0q!f'
metadb_dbname = 'cmdb'

# backup status
BACKUP_OK   = 0
BACKUP_FAIL = 1
BACKUP_ING  = 2

# prepare status
PREPARE_OK   = 0
PREPARE_FAIL = 1

# print to screen
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

m_backup_method = {'xtra': 1, 'offline': 2, 'delay': 3}
m_backup_period = {'day': 1, 'week': 2, 'month': 3}
backup_status_suffix = {BACKUP_OK: '', BACKUP_FAIL: '_fail', BACKUP_ING: '_baking'}
log_base_dir = '/var/log/mysql_backup/'

log_map = {}
log_file = {'filename': 'mysql_backup'}

def log(log_msg, level='debug', filename=''):
    try:
        if not filename:
            filename = log_file['filename']
        if filename in log_map:
            tmp_log=log_map.get(filename)
        else:
            tmp_log=logging.getLogger(filename)
            tmp_log.setLevel(logging.DEBUG)
            tmp_formatter = logging.Formatter(" %(asctime)s - %(message)s")
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

# log backup status info into metadb
def dblog(dblog_msg, dblog_status):
    try:
        if dblog_status is False:
            return
        dblog_msg['extra_info'] = mysqllib.escape_string(dblog_msg['extra_info'])
        cond_list = ["%s='%s'" % (k, v) for k, v in dblog_msg.items()]
        sql = '''replace into db_backup_status set %s;''' % ','.join(cond_list)
        mysqlbase = mysqllib.MySQLBase(metadb_host, metadb_port, backup_user, backup_passwd, db=metadb_dbname)
        mysqlbase.query(sql, fetch=False)
    except Exception, e:
        log('dblog failed for %s' % str(e), level='error')

def check_ip(ip):
    try:
        pat = r'^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$'
        if not re.match(pat, ip):
            return False
        return True
    except Exception, e:
        raise e

def arg_parse():
    t_method = ('xtra', 'offline', 'delay')
    t_period = ('day', 'week', 'month')
    parse = argparse.ArgumentParser(description='Mysql backup')
    parse.add_argument('--port', '-P', type=int, required=True, help='mysql port')
    parse.add_argument('--host', '-H', required=True, help='local host like 192.168.7.29')
    parse.add_argument('--tag', '-T', required=True, help='product name like villa room bee')
    parse.add_argument('--method', '-m', default='xtra', help='mysql backup method, include %s' % ', '.join(t_method))
    parse.add_argument('--defaults-file', '-f', help='mysql config file, it will get from ps result if not specify')
    parse.add_argument('--socket', '-S', help='mysql unix socket, it will get from ps result if not specify')
    parse.add_argument('--basedir', '-b', help='mysql basedir, it will get from ps result if not specify')
    parse.add_argument('--datadir', '-d', help='mysql datadir, it will get from ps result if not specify')
    parse.add_argument('--period', '-p', default='day', help='backup period, include %s' % ', '.join(t_period))
    parse.add_argument('--parallel', type=int, default=1, help='number of threads, default 1')
    parse.add_argument('--throttle', type=int, default=500, help='number of IO operations per second, default 500')
    parse.add_argument('--backup-dir', help='target backup dir, default /backupnfs/backup/{$period}/mysql{$port}/{CURRENT_DATE}/db{$port}')
    parse.add_argument('--prepare', default=True,action='store_true', help='prepare backup in backup-dir')
    parse.add_argument('--delay', default='8h', help='how far the slave should lag its master when use delay backup method, default 3h')
    parse.add_argument('--dblog-status', default=True,action='store_true', help='log backup status info into metadb')
    options = parse.parse_args() 
    if options.method not in t_method:
        parse.error('argument --method/-m must be in %s' % ', '.join(t_method))
    if options.period not in t_period:
        parse.error('argument --period/-p must be in %s' % ', '.join(t_period))
    if check_ip(options.host) is False:
        parse.error('host %s is illegal' % options.host)
    return parse, options

def exec_cmd(cmd):
    try:
        pipe = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, stdin=subprocess.PIPE)
        stdout, stderr = pipe.communicate()
        if pipe.returncode == 0:
            return {'status': 0, 'result': stdout.strip()}
        elif pipe.returncode == 1 and not stderr:
            return {'status': 0, 'result': ''}
        else:
            raise Exception, 'exec %s error, returncode: %s, stderr: %s' % (cmd, pipe.returncode, stderr)
    except Exception, e:
        raise e

def backup_exec(cmd):
    try:
        file_name = log_base_dir + log_file['filename'] + '.log'
	print cmd
        with open(file_name, 'a+') as fd:  # use file to avoid out pipe overflow
            pipe = subprocess.Popen(cmd, stdout=fd,stdin=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
            while pipe.poll() == None:
                #log(pipe.stdout.readline().strip())
		print pipe.stderr.readline().strip()
                time.sleep(5)
	stdout,stderr = pipe.communicate()
	print "ERROR1",stderr
	print "ERROR1",stdout
        if pipe.returncode != 0:
            	rt={'status':-1,'result':stderr}
		print rt
		return rt
        rt={'status': 0, 'result': 'execute innobackupex success'}
	print rt
	return rt
    except Exception, e:
	print "ERROR1",traceback.print_exc()
        raise e

def delaybackup_exec(cmd):
    try:
        pipe = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, stdin=subprocess.PIPE)
        for i in range(5):
            if pipe.poll() and pipe.returncode != 0:
                raise Exception, 'exec %s error, returncode: %s, stderr: %s' % (cmd, pipe.returncode, pipe.stderr.readline())
            time.sleep(1)
        return {'status': 0, 'result': 'execute delaybackup success'}
    except Exception, e:
        raise e

# get size by du
def du_size(dir):
    try:
        cmd = "du -bs %s | awk {'print $1/1024/1024'}" % dir
        ret = exec_cmd(cmd)
        if ret['status'] == 0 and ret['result']:
            return int(float(ret['result']))
        return 0
    except Exception, e:
        log('get %s size failed for %s' % (dir, str(e)))
        return 0

# recurse link
def recurse_link(source_path, target_path):
    try:
        if os.path.isdir(source_path) is True:
            if os.path.exists(target_path) is False:
                os.makedirs(target_path)
                log('backup link: makedirs %s' % target_path)
            for p_dir, c_dirs, files in os.walk(source_path):
                for c_dir in c_dirs:
                    pc_dir = '%s/%s' % (p_dir, c_dir)
                    tmp_dir = pc_dir.replace(source_path, target_path)
                    if os.path.exists(tmp_dir) is False:
                        os.makedirs(tmp_dir)
                        log('backup link: makedirs %s' % tmp_dir)
                for file in files:
                    source_link = '%s/%s' % (p_dir, file)
                    target_link = source_link.replace(source_path, target_path)
                    if os.path.exists(target_link) is False:
                        os.link(source_link, target_link)
                        log('backup link: %s link to %s' % (target_link, source_link))
        else:
            os.link(source_path, target_path)
            log('backup link: %s link to %s' % (target_path, source_path))
        return True
    except Exception, e:
        log('recurse link %s to %s failed for %s' % (source_path, target_path, str(e)), level='error')
        return False

# mysql instance existence check
def mysql_ins_check(port):
    try:
        cmd = 'ps aux | grep -v grep | grep -v python | grep %s | grep mysqld | wc -l' % port
        ret = exec_cmd(cmd)
        if ret['status'] == 0 and int(ret['result']) > 0:
            return True
        return False
    except Exception, e:
        return False

# get specific parameter in ps result
def get_ps_param(ps_result, param_k):
    try:
        ps_list = ps_result.split()
        pt = re.compile(r'.*%s.*' % param_k)
        result = ''
        for i in ps_list:
            if pt.search(i) and '=' in i:
                result = i.split('=')[1]
                return result
        if not result:
            raise Exception, 'get %s from ps failed' % param_k
    except Exception, e:
        raise e

# get mysql base directory
def get_base_dir(port):
    try:
        cmd = 'ps aux | grep -Ev "grep|python|innobackupex|xtrabackup" | grep %s | grep mysql | grep basedir' % port
        ret = exec_cmd(cmd)
        if ret['status'] == 0:
            return get_ps_param(ret['result'], 'basedir')
    except Exception, e:
        raise e

# get mysql data directory
def get_data_dir(port):
    try:
        cmd = 'ps aux | grep -Ev "grep|python|innobackupex|xtrabackup" | grep %s | grep mysql | grep datadir' % port
        ret = exec_cmd(cmd)
        if ret['status'] == 0:
            return get_ps_param(ret['result'], 'datadir')
    except Exception, e:
        raise e

# get mysql unix socket file directory
def get_socket_dir(port):
    try:
        cmd = 'ps aux | grep -Ev "grep|python|innobackupex|xtrabackup" | grep %s | grep mysql | grep socket' % port
        ret = exec_cmd(cmd)
        if ret['status'] == 0:
            return get_ps_param(ret['result'], 'socket')
    except Exception, e:
        raise e

# get mysql defaults file directory
def get_defaults_file_dir(port):
    try:
        cmd = 'ps aux | grep -Ev "grep|python|innobackupex|xtrabackup" | grep %s | grep mysqld | grep defaults-file' % port
        ret = exec_cmd(cmd)
        if ret['status'] == 0:
            return get_ps_param(ret['result'], 'defaults-file')
    except Exception, e:
        return '/etc/my.cnf'

# xtrabackup params check, create backup dir if it does not exist
def xtra_check(params, current_date):
    try:
        port = params['port']
        tag = params['tag']
        defaults_file = params['defaults-file'] if params['defaults-file'] else get_defaults_file_dir(port)
        if os.path.exists(defaults_file) is False:
            raise IOError, 'no such file or directory: %s' % defaults_file
        socket = params['socket'] if params['socket'] else get_socket_dir(port)
	p=subprocess.Popen('/bin/mount|grep nfs|grep dbbackup',stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
	stdout,stderr=p.communicate()
	if len(stdout)==0:
		return {'status':-1,'result':'No Mount Dir'}
        if os.path.exists(socket) is False:
            raise IOError, 'no such file or directory: %s' % socket
	backup_dir_prefix='/data/dbbackup/%s/%s/%s' % (params['period'],tag, current_date)
        if os.path.exists(backup_dir_prefix):
		return {'status':-1,'result':'Data Dir is Exist!'}
        backup_pdir = params['backup-dir'] if params['backup-dir'] else '/data/dbbackup/%s/%s/%s_baking' % (params['period'],tag, current_date)
        if os.path.exists(backup_pdir) is False:
            os.makedirs(backup_pdir)
        backup_dir = '%s/mysql%d' % (backup_pdir, port)
        return {'status': 0, 'result': {'defaults-file': defaults_file, 'socket': socket, 'backup-dir': backup_dir}}
    except Exception, e:
        raise e

# offlinebackup params check
def offline_check(params, current_date):
    try:
        port = params['port']
        basedir = params['basedir'] if params['basedir'] else get_base_dir(port)
        if os.path.exists(basedir) is False:
            raise IOError, 'no such file or directory: %s' % basedir
        datadir = params['datadir'] if params['datadir'] else get_data_dir(port)
        if os.path.exists(datadir) is False:
            raise IOError, 'no such file or directory: %s' % datadir
        defaults_file = params['defaults-file'] if params['defaults-file'] else get_defaults_file_dir(port)
        if os.path.exists(defaults_file) is False:
            raise IOError, 'no such file or directory: %s' % defaults_file
        socket = params['socket'] if params['socket'] else get_socket_dir(port)
        if os.path.exists(socket) is False:
            raise IOError, 'no such file or directory: %s' % socket
        backup_pdir = params['backup-dir'] if params['backup-dir'] else '/backupnfs/backup/%s/mysql%d/%s_baking' % (params['period'],
                      port, current_date)
        if os.path.exists(backup_pdir) is False:
            os.makedirs(backup_pdir)
        backup_dir = '%s/db%d' % (backup_pdir, port)
        return {'status': 0, 'result': {'basedir': basedir, 'datadir': datadir, 'defaults-file': defaults_file, 
                'socket': socket, 'backup-dir': backup_dir}}
    except Exception, e:
        raise e

# delaybackup instance check
def delay_ins_check(port):
    try:
        cmd = 'ps aux | grep -v grep | grep -v python | grep pt-slave-delay | grep %s' % port
        ret = exec_cmd(cmd)
        if ret['status'] == 0:
            if ret['result']:
                result = {'pid': ret['result'].split()[1], 'delay': get_ps_param(ret['result'], 'delay')}
                return {'status': 1, 'result': result}
            else:
                return {'status': 0, 'result': {}}
    except Exception, e:
        raise e

# delaybackup params check
def delay_check(params):
    try:
        port = params['port']
        defaults_file = params['defaults-file'] if params['defaults-file'] else get_defaults_file_dir(port)
        if os.path.exists(defaults_file) is False:
            raise IOError, 'no such file or directory: %s' % defaults_file
        socket = params['socket'] if params['socket'] else get_socket_dir(port)
        if os.path.exists(socket) is False:
            raise IOError, 'no such file or directory: %s' % socket
        return {'status': 0, 'result': {'defaults-file': defaults_file, 'socket': socket}}
    except Exception, e:
        raise e

# mysql start
def mysql_start(basedir, defaults_file, host, port, socket):
    try:
        cmd = '%s/bin/mysqld_safe --defaults-file=%s > /dev/null 2>&1 &' % (basedir, defaults_file)
        exec_cmd(cmd)
    except Exception, e:
        raise 'mysql start failed for %s' % str(e)
    finally:
        for i in range(10):
            time.sleep(60)
            if mysql_connection_check(host, port, socket) is True:
                return True
        return False

# mysql stop
def mysql_stop(basedir, socket):
    try:
        cmd = "%s/bin/mysqladmin -u%s -p'%s' -S %s shutdown" % (basedir, backup_user, backup_passwd, socket)
        exec_cmd(cmd)
    except Exception, e:
        raise 'mysql stop failed for %s' % str(e)

# mysql connection check
def mysql_connection_check(host, port, socket):
    try:
        mysqlbase = mysqllib.MySQLBase(host, port, backup_user, backup_passwd, unix_socket=socket)
        mysqlbase.query('select 1;')
        return True
    except Exception, e:
        return False

# mysql io and sql threads check
def mysql_threads_check(host, port, socket):
    try:
        mysqlbase = mysqllib.MySQLBase(host, port, backup_user, backup_passwd, unix_socket=socket)
        rows = mysqlbase.query('show slave status;')
        if rows:
            if rows[0]['Slave_IO_Running'].lower() == 'yes' and rows[0]['Slave_SQL_Running'].lower() == 'yes':
                return {'status': 0, 'result': {'Slave_IO_Running': rows[0]['Slave_IO_Running'], 
                        'Slave_SQL_Running': rows[0]['Slave_SQL_Running']}}
            else:
                return {'status': -1, 'result': {'Last_Errno': rows[0]['Last_Errno'], 'Last_Error': rows[0]['Last_Error'],
                        'Slave_IO_Running': rows[0]['Slave_IO_Running'], 'Slave_SQL_Running': rows[0]['Slave_SQL_Running']}}
    except Exception, e:
        raise e

# check io and sql threads for starting slave
def start_slave(host, port, socket):
    try:
        mysqlbase = mysqllib.MySQLBase(host, port, backup_user, backup_passwd, unix_socket=socket)
        rows = mysqlbase.query('show slave status;')
        if rows:
            if rows[0]['Slave_IO_Running'].lower() == 'yes' and rows[0]['Slave_SQL_Running'].lower() == 'yes':
                pass
            else:
                mysqlbase.query('start slave;', fetch=False)
                time.sleep(5)
                return mysqlbase.query('show slave status;')
    except Exception, e:
        raise e

# rename backup directory to mark backup status
# sample: /data/dbbackup/day/test/20150909[_baking|_fail]/mysql3306
def backup_rename(dir, status):
    try:
        match = re.match(r'.*/dbbackup/.*/(\d+)_([a-z]+)(.*)/', dir)
        if not match:
            return dir
	print "MATCH:",match.groups()
        dir_date, dir_db = match.groups()[0:2]
        new_dir_date = '%s%s' % (dir_date, backup_status_suffix[status])
	print dir
	print new_dir_date
        rename_dir = dir.replace('%s_%s'%(dir_date, dir_db), new_dir_date)
	print rename_dir
        os.rename('/'.join(dir.split('/')[0:-1]), '/'.join(rename_dir.split('/')[0:-1]))
        return rename_dir
    except Exception, e:
        log('rename backup directory failed for %s' % str(e), level='error')
        return dir

# copy defaults file
def cp_defaults_file(defaults_file, backup_dir, port):
    try:
        cmd = '\cp %s %s/my%s.cnf' % (defaults_file, backup_dir, port)
        exec_cmd(cmd)
        log(cmd)
    except Exception, e:
        log('copy defaults file failed for %s' % str(e), level='error')

# do prepare on backup
def xtra_prepare(backup_dir, prepare=True):
    try:
        if prepare is True:
            cmd = '/usr/bin/innobackupex '
            cmd += '--defaults-file=backup-my.cnf '
            cmd += '--apply-log --redo-only '
            cmd += '--use-memory=4GB '
            cmd += backup_dir
            backup_exec(cmd)
            return {'status': 0, 'result': 'prepare success'}
        else:
            return {'status': -1, 'result': 'prepare ignore'}
    except Exception, e:
        return {'status': -1, 'result': str(e)}

# use innobackupex to do backup action and transfer through nfs
def xtra_backup(params, dblog_status):
    try:
        log_file['filename'] = 'mysql_%d_%s_backup_%s_%s' % (params['port'], params['method'], params['period'], params['current_date'])
        start_time = params['start_time']
        dblog_msg = {'port': params['port'], 'host': params['host'], 'backup_method': m_backup_method[params['method']], 
                     'backup_period': m_backup_period[params['period']], 'start_time': start_time, 'end_time': '0000-00-00 00:00:00', 
                     'backup_size': 0, 'back_status': BACKUP_ING, 'prepare_status': PREPARE_FAIL, 'extra_info': ''}
        dblog(dblog_msg, dblog_status)
        log('params of mysql backup %s' % params)
        check_ret = xtra_check(params, params['current_date'])
	print check_ret
        if check_ret['status'] == 0:
            backup_dir = check_ret['result']['backup-dir']
	    print backup_dir
            cmd = '/usr/bin/innobackupex '
            cmd += '--defaults-file=%s ' % check_ret['result']['defaults-file']
            cmd += '--socket=%s ' % check_ret['result']['socket']
            #cmd += '--parallel=%d --throttle=%d ' % (params['parallel'], params['throttle'])
            # xtrabackup 2.4.1 bug, cannot add parameter --throttle
            cmd += '--parallel=%d ' % params['parallel']
            cmd += "--user=%s --password='%s' " % (backup_user, backup_passwd)
            cmd += '--slave-info --no-timestamp '
            cmd += backup_dir
            bk_rt=backup_exec(cmd)
	    if bk_rt['status']!=0:
	    	return bk_rt	
            cp_defaults_file(check_ret['result']['defaults-file'], backup_dir, params['port'])
            backup_size = du_size(backup_dir)
            dblog_msg = {'port': params['port'], 'host': params['host'], 'backup_method': m_backup_method[params['method']],
                         'backup_period': m_backup_period[params['period']], 'start_time': start_time, 'end_time': '0000-00-00 00:00:00', 
                         'backup_size': backup_size, 'back_status': BACKUP_OK, 'prepare_status': PREPARE_FAIL, 'extra_info': ''}
	    print dblog_msg
	    print dblog_status
            dblog(dblog_msg, dblog_status)
            pre_ret = xtra_prepare(backup_dir, params['prepare'])
            end_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if pre_ret['status'] != 0:
                prepare_status = PREPARE_FAIL
                extra_info = pre_ret['result']
            else:
                prepare_status = PREPARE_OK
                extra_info = ''
            backup_size = du_size(backup_dir)
            dblog_msg = {'port': params['port'], 'host': params['host'], 'backup_method': m_backup_method[params['method']],
                         'backup_period': m_backup_period[params['period']], 'start_time': start_time, 'end_time': end_time, 
                         'backup_size': backup_size, 'back_status': BACKUP_OK, 'prepare_status': prepare_status, 'extra_info': extra_info}
            dblog(dblog_msg, dblog_status)
            backup_rename(backup_dir, BACKUP_OK)
    except Exception, e:
	print "ERROR:",traceback.print_exc()
        log(str(e), level='error')
        end_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        dblog_msg = {'port': params['port'], 'host': params['host'], 'backup_method': m_backup_method[params['method']], 
                     'backup_period': m_backup_period[params['period']], 'start_time': start_time, 'end_time': end_time, 
                     'backup_size': 0, 'back_status': BACKUP_FAIL, 'prepare_status': PREPARE_FAIL, 'extra_info': str(e)}
        dblog(dblog_msg, dblog_status)
        backup_rename(backup_dir, BACKUP_FAIL)
	print traceback.print_exc()
        raise e

# stop mysql and copy data dir to backup
def offline_backup(params, dblog_status):
    try:
        log_file['filename'] = 'mysql_%d_%s_backup_%s_%s' % (params['port'], params['method'], params['period'], params['current_date'])
        start_time = params['start_time']
        backup_size = 0
        dblog_msg = {'port': params['port'], 'host': params['host'], 'backup_method': m_backup_method[params['method']],
                     'backup_period': m_backup_period[params['period']], 'start_time': start_time, 'end_time': '0000-00-00 00:00:00',
                     'backup_size': backup_size, 'back_status': BACKUP_ING, 'prepare_status': PREPARE_OK, 'extra_info': ''}
        dblog(dblog_msg, dblog_status)
        log('params of mysql backup %s' % params)
        ins_check_ret = mysql_ins_check(params['port'])
        if ins_check_ret is False:
            raise Exception, 'mysql instance does not exist'
        check_ret = offline_check(params, params['current_date'])
        if check_ret['status'] == 0:
            backup_dir = check_ret['result']['backup-dir']
            log('mysql instance stop...')
            mysql_stop(check_ret['result']['basedir'], check_ret['result']['socket'])
            cmd = '\cp -rv %s %s' % (check_ret['result']['datadir'], backup_dir)
            backup_exec(cmd)
            cp_defaults_file(check_ret['result']['defaults-file'], backup_dir, params['port'])
            end_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            backup_size = du_size(backup_dir)
            dblog_msg = {'port': params['port'], 'host': params['host'], 'backup_method': m_backup_method[params['method']],
                         'backup_period': m_backup_period[params['period']], 'start_time': start_time, 'end_time': end_time,
                         'backup_size': backup_size, 'back_status': BACKUP_OK, 'prepare_status': PREPARE_OK, 'extra_info': ''}
            dblog(dblog_msg, dblog_status)
            backup_rename(backup_dir, BACKUP_OK)
    except Exception, e:
        log(str(e), level='error')
        end_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        dblog_msg = {'port': params['port'], 'host': params['host'], 'backup_method': m_backup_method[params['method']],
                     'backup_period': m_backup_period[params['period']], 'start_time': start_time, 'end_time': end_time,
                     'backup_size': backup_size, 'back_status': BACKUP_FAIL, 'prepare_status': PREPARE_FAIL, 'extra_info': str(e)}
        dblog(dblog_msg, dblog_status)
        if ins_check_ret is True:
            backup_rename(backup_dir, BACKUP_FAIL)
    finally:
        if mysql_start(check_ret['result']['basedir'], check_ret['result']['defaults-file'], params['host'], 
                       params['port'], check_ret['result']['socket']) is True:
            log('mysql start success')
            start_slave_ret = start_slave(params['host'], params['port'], check_ret['result']['socket'])
            if start_slave_ret:
                if start_slave_ret[0]['Slave_IO_Running'].lower() == 'yes' and start_slave_ret[0]['Slave_SQL_Running'].lower() == 'yes':
                    log('slave start... Slave_IO_Running: Yes, Slave_SQL_Running: Yes')
                else:
                    log('slave start... Slave_IO_Running: %s, Slave_SQL_Running: %s, Last_Errno: %s, Last_Error: %s' 
                        % (start_slave_ret[0]['Slave_IO_Running'], start_slave_ret[0]['Slave_SQL_Running'], 
                        start_slave_ret[0]['Last_Errno'], start_slave_ret[0]['Last_Error']))
                    end_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    extra_info = 'start slave failed'
                    dblog_msg = {'port': params['port'], 'host': params['host'], 'backup_method': m_backup_method[params['method']],
                                 'backup_period': m_backup_period[params['period']], 'start_time': start_time, 'end_time': end_time,
                                 'backup_size': backup_size, 'back_status': BACKUP_FAIL, 'prepare_status': PREPARE_FAIL, 'extra_info': extra_info}
                    dblog(dblog_msg, dblog_status)
        else:
            log('mysql start failed')
            end_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            extra_info = 'mysql start failed'
            dblog_msg = {'port': params['port'], 'host': params['host'], 'backup_method': m_backup_method[params['method']],
                         'backup_period': m_backup_period[params['period']], 'start_time': start_time, 'end_time': end_time,
                         'backup_size': backup_size, 'back_status': BACKUP_FAIL, 'prepare_status': PREPARE_FAIL, 'extra_info': extra_info}
            dblog(dblog_msg, dblog_status)

# use pt-slave-delay to do delay backup action
def delay_backup(params, dblog_status):
    try:
        log_file['filename'] = 'mysql_%d_%s_backup' % (params['port'], params['method'])
        start_time = params['start_time']
        dblog_msg = {'port': params['port'], 'host': params['host'], 'backup_method': m_backup_method[params['method']],
                     'backup_period': m_backup_period[params['period']], 'start_time': start_time, 'end_time': '0000-00-00 00:00:00', 
                     'backup_size': 0, 'back_status': BACKUP_ING, 'extra_info': ''}
        dblog(dblog_msg, dblog_status)
        log('params of mysql backup %s' % params)
        check_ret = delay_check(params)
        exec_flag = True
        if check_ret['status'] == 0:
            ins_check_ret = delay_ins_check(params['port'])
            if ins_check_ret['status'] == 1:
                if ins_check_ret['result']['delay'] == params['delay']:
                    exec_flag = False
                else:
                    cmd = 'kill %s' % ins_check_ret['result']['pid']
                    exec_cmd(cmd)
        if exec_flag is True:
            start_slave(params['host'], params['port'], check_ret['result']['socket'])
            cmd = '/usr/bin/pt-slave-delay '
            cmd += '--defaults-file=%s ' % check_ret['result']['defaults-file']
            cmd += '--socket=%s ' % check_ret['result']['socket']
            cmd += '--user=%s --password=%s ' % (backup_user, backup_passwd)
            cmd += '--delay=%s --log=%s%s.log ' % (params['delay'], log_base_dir, log_file['filename'])
            cmd += '--daemonize'
            delaybackup_exec(cmd)
        end_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        dblog_msg = {'port': params['port'], 'host': params['host'], 'backup_method': m_backup_method[params['method']],
                     'backup_period': m_backup_period[params['period']], 'start_time': start_time, 'end_time': end_time, 
                     'backup_size': 0, 'back_status': BACKUP_OK, 'extra_info': ''}
        dblog(dblog_msg, dblog_status)
    except Exception, e:
        log(str(e), level='error')
        end_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        dblog_msg = {'port': params['port'], 'host': params['host'], 'backup_method': m_backup_method[params['method']],
                     'backup_period': m_backup_period[params['period']], 'start_time': start_time, 'end_time': end_time, 
                     'backup_size': 0, 'back_status': BACKUP_FAIL, 'extra_info': str(e)}
        dblog(dblog_msg, dblog_status)
        raise e

# link backup if the other period backup has done
def link_backup(params, dblog_status):
    try:
        log_file['filename'] = 'mysql_%d_%s_backup_%s_%s' % (params['port'], params['method'], params['period'], params['current_date'])
        log('params of mysql backup %s' % params)
        backup_pdir = params['backup-dir'] if params['backup-dir'] else '/backupnfs/backup/%s/mysql%d/%s' % (params['period'], 
                       params['port'], params['current_date'])
        start_time = params['start_time']
        dblog_msg = {'port': params['port'], 'host': params['host'], 'backup_method': m_backup_method[params['method']],
                     'backup_period': m_backup_period[params['period']], 'start_time': start_time, 'end_time': '0000-00-00 00:00:00',
                     'backup_size': 0, 'back_status': BACKUP_ING, 'extra_info': ''}
        dblog(dblog_msg, dblog_status)
        tmp_periods = m_backup_period.keys()
        tmp_periods.remove(params['period'])
        check_dirs = []
        check_baking_dirs = []
        for tmp_period in tmp_periods:
            tmp_dir = backup_pdir.replace(params['period'], tmp_period)
            check_dirs.append(tmp_dir)
            check_baking_dirs.append('%s%s' % (tmp_dir, backup_status_suffix[BACKUP_ING]))
        for check_baking_dir in check_baking_dirs:
            while os.path.exists(check_baking_dir) is True:
                log('waiting for %s...' % check_baking_dir)
                time.sleep(120)
        for check_dir in check_dirs:
            if os.path.exists(check_dir) is True:
                if recurse_link(check_dir, backup_pdir) is True:
                    backup_size = du_size(backup_pdir)
                    end_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    dblog_msg = {'port': params['port'], 'host': params['host'], 'backup_method': m_backup_method[params['method']],
                                 'backup_period': m_backup_period[params['period']], 'start_time': start_time, 'end_time': end_time,
                                 'backup_size': backup_size, 'back_status': BACKUP_OK, 'extra_info': ''}
                    dblog(dblog_msg, dblog_status)
                    return True
        return False
    except Exception, e:
        log('link backup failed for %s' % str(e), level='error')
        return False

def main():
    parse, opts = arg_parse()
    params = {}
    now = datetime.datetime.now()
    current_date = now.strftime('%Y%m%d')
    start_time = now.strftime('%Y-%m-%d %H:%M:%S')
    if opts.method == 'xtra':
        params = {"tag":opts.tag,'port': opts.port, 'host':opts.host, 'defaults-file': opts.defaults_file, 
                  'socket': opts.socket, 'method': opts.method, 'parallel': opts.parallel, 
                  'throttle': opts.throttle, 'period': opts.period, 'backup-dir': opts.backup_dir, 
                  'prepare': opts.prepare, 'start_time': start_time, 'current_date': current_date}
	print opts.dblog_status
        if link_backup(params, opts.dblog_status) is False:
	    print opts.dblog_status
            xtra_backup(params, opts.dblog_status)
    elif opts.method == 'offline':
        params = {'port': opts.port, 'host':opts.host, 'defaults-file': opts.defaults_file,
                  'socket': opts.socket, 'method': opts.method, 'period': opts.period, 
                  'basedir': opts.basedir, 'datadir': opts.datadir, 'backup-dir': opts.backup_dir,
                  'start_time': start_time, 'current_date': current_date}
        if link_backup(params, opts.dblog_status) is False:
            offline_backup(params, opts.dblog_status)
    elif opts.method == 'delay':
        params = {'port': opts.port, 'host':opts.host, 'defaults-file': opts.defaults_file, 
                  'socket': opts.socket, 'method': opts.method, 'delay': opts.delay, 'period': opts.period, 
                  'start_time': start_time}
        delay_backup(params, opts.dblog_status)
    else:
        pass

if __name__ == '__main__':
    main()
