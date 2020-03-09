#! /usr/bin/python2.7
# encoding=utf-8
__author__ = 'zolker'

'''
Cleanup outdated and fail mysql backup.
'''

import os
import sys
import re
import itertools
import subprocess
#import mysqllib
import MySQLdb
from warnings import filterwarnings
import logging
filterwarnings('ignore', category = MySQLdb.Warning)
sys.path.append('/etc/db_tools')
from mysqllib import *
from syslib import *
reload(sys)
sys.setdefaultencoding('utf-8')


metadb_host = '10.110.17.6'
metadb_port = 3307
metadb_user = 'db_admin'
metadb_passwd = 'BZs*gIyVeH4o0q!f'
metadb_dbname = 'cmdb'

# backup status
BACKUP_OK   = 0
BACKUP_FAIL = 1
BACKUP_ING  = 2

backup_base_dir = ['/data/dbbackup']
m_backup_period = {'day': 1, 'week': 2, 'month': 3}
m_backup_method = {'online': 1, 'offline': 2, 'delay': 3}
log_map = {}

REMAINS = 3
TRUNCATE_SIZE = 20 # unit M
default_port=3306
def log(log_msg, level='debug', filename='mysql_backup_cleanup'):
    try:
        if filename in log_map:
            tmp_log=log_map.get(filename)
        else:
            tmp_log=logging.getLogger(filename)
            tmp_log.setLevel(logging.DEBUG)
            tmp_formatter = logging.Formatter(" %(asctime)s - %(message)s")
            log_base_dir = '/data/logs/'
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

def exec_cmd(cmd):
    try:
        pipe = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, stdin=subprocess.PIPE)
        stdout, stderr = pipe.communicate()
        if pipe.returncode != 0:
            raise Exception, 'exec %s error, returncode: %s, stderr: %s' % (cmd, pipe.returncode, stderr)
        return {'status': 0, 'result': stdout.strip()}
    except Exception, e:
        raise e

def get_file_size(file_path):
    try:
        return int(os.path.getsize(file_path)/1024/1024)
    except Exception, e:
        raise e

def rm_file(file_path):
    try:
        cmd = 'rm -rf %s' % file_path
        return exec_cmd(cmd)
    except Exception, e:
        raise e

def truncate_file(file_path):
    try:
        if os.path.isdir(file_path) is True:
            return
        truncate_times = get_file_size(file_path)/TRUNCATE_SIZE
        for i in range(truncate_times):
            cmd = 'truncate -s -%dM %s' % (TRUNCATE_SIZE, file_path)
            exec_cmd(cmd)
        rm_file(file_path)
    except Exception, e:
        raise e

def truncate_directory(directory):
    try:
        for p_dir, c_dirs, c_files in os.walk(directory):
            for c_file in c_files:
                file_path = '%s/%s' % (p_dir, c_file)
                truncate_file(file_path)
        rm_file(directory)
    except Exception, e:
        raise 'truncate directory failed for %s' % str(e)

# get backup remains from metadata db
def get_remains(port, backup_items):
    try:
        if not default_port or not backup_items:
            return REMAINS
        sql = """ select port, keep_days as backup_remains from cmdb.redis_backup_policy where port=%d limit 1;""" % (int(port))
        mysqlbase = MySQLBase(metadb_host, metadb_port, metadb_user, metadb_passwd, db=metadb_dbname)
        rows = mysqlbase.query(sql)
        if rows:
            return rows[0]['backup_remains']
        return REMAINS
    except Exception, e:
	print traceback.print_exc()
        raise 'get backup remains failed for %s' % str(e)

# get mysql port and backup period in bakcup dir
def get_port_period(dir):
    try:
        match = re.match(r'.*(day|week|month)/(.*)', dir)
        if match is None:
            return {'period': None, 'port': None}
        groups = match.groups()
        return {'period': groups[0], 'tag': groups[1]}
    except Exception, e:
        raise e

# walk backup dir by date
# path sample: /data1/backup/day/mysql3306/20150909[_baking|_fail]
def backup_dir_walk():
    try:
        #periods = m_backup_period.keys()
	periods=['redis']
        period_dirs = ['/'.join(i) for i in itertools.product(backup_base_dir, periods)]
        redisport_dirs = []
        for period_dir in period_dirs:
            if os.path.exists(period_dir) is True:
                tmp_dirs = os.listdir(period_dir)
                if tmp_dirs:
                    redisport_dirs.extend(['%s/%s' % (period_dir, i) for i in tmp_dirs])
        walk_result = {}
        for redisport_dir in redisport_dirs:
            if os.path.isdir(redisport_dir) is True:
                tmp_dirs = os.listdir(redisport_dir)
                #ret = get_port_period(redisport_dir)
                walk_result[redisport_dir] = {'period': 'day', 'port': redisport_dir.split('/')[-1], 'backups': tmp_dirs}
        return walk_result
    except Exception, e:
        raise 'backup dir walk failed for %s' % str(e)

def get_truncate_backup(backup_dir, backup_items):
    try:
	print backup_items
        remains = get_remains(backup_items['port'], backup_items)
        backup_des = {BACKUP_OK: '', BACKUP_FAIL: 'fail', BACKUP_ING: 'baking'}
        backup_ok_list = []
        backup_fail_list = []
        for backup in backup_items['backups']:
            if backup_des[BACKUP_FAIL] in backup:
                backup_fail_list.append(backup)
            elif backup_des[BACKUP_ING] in backup:
                pass
            else:
                backup_ok_list.append(backup)
        outdated_backups = []
        if len(backup_ok_list) > remains:
            outdated_backups = sorted(backup_ok_list, reverse=True)[int(remains):]
        truncate_backups = backup_fail_list + outdated_backups
        if truncate_backups:
            return ['%s/%s' % (backup_dir, truncate_backup) for truncate_backup in truncate_backups]
        return []
    except Exception, e:
	print traceback.print_exc()
        raise 'get truncate backup failed for %s' % str(e)

def main():
    try:
        log('start redis backups cleaning...')
        walk_ret = backup_dir_walk()
	#print walk_ret
        #log('backup dir walk result: %s' % str(walk_ret))
        for backup_dir, backup_items in walk_ret.items():
            try:
		print backup_dir,backup_items
                truncate_backups = get_truncate_backup(backup_dir, backup_items)
		print truncate_backups
                for truncate_backup in truncate_backups:
                    try:
                        #truncate_directory(truncate_backup) # truncate is not suitable for backup link
                        rm_file(truncate_backup)
                        log('remove %s done' % truncate_backup)
                    except Exception, e:
                        log(str(e), level='error')
            except Exception, e:
		print traceback.print_exc()
                log(str(e), level='error')
        log('mysql backups clean done')
    except Exception, e:
        log(str(e), level='error')

if __name__ == '__main__':
    main()
