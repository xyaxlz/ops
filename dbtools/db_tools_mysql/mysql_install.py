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
sys.path.append('/etc/db_tools')
from mysqllib import *
from syslib import *
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
    parse.add_argument('--host', '-H', default='',help='host ip')
    parse.add_argument('--engine', '-e', default='innodb',help='mysql engine')
    parse.add_argument('--tag', '-t', default='mysql',help='mysql tag')
    parse.add_argument('--role', '-r', default='master',help='mysql tag')
    parse.add_argument('--datadir', '-d', default='data',help='mysql datadir')
    parse.add_argument('--buffersize', '-b', default='1G',help='buffer pool:10G')
    return parse, parse.parse_args()


###################################
##main
#if __name__ == '__main__':

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
    db_tag=opts.tag
    datadir='/%s'%opts.datadir
    db_role=opts.role
    db_buffer=opts.buffersize
    db_host=opts.host
    #rpm_name="%s-%s.x86_64"%(db_tag,db_version)
    #mysql_rpm_status='yum list|grep -i %s'%str(rpm_name)
    #temp_rt=run_command(mysql_rpm_status)[0].split()
    mysqld_dir="/usr/local/%s-%s/bin/mysqld"%(db_tag,db_version)
    if  not os.path.isfile(mysqld_dir):
    	print "mysqld is not exists!"
	sys.exit()
    db_data_dir='%s/mysql%s'%(datadir,str(db_port))
    data_base_dir='%s/mysql%s/mysqldata'%(datadir,str(db_port))
    rt={}
    data_exist_flag=0
    if db_host!="127.0.0.1" and  db_host!='':
    	exist_cmd='ls  -d %s  '%(db_data_dir)
	exist_flag=sys_cmd(db_host,exist_cmd)
	if exist_flag['status']==-1:
		exist_flag=False
    else:
    	exist_flag=os.path.exists(db_data_dir)
    if not exist_flag: 
	if db_host!="127.0.0.1" and  db_host!='':
		mkdir_cmd='mkdir -p %s'%(db_data_dir)
		temp_rt=sys_cmd(db_host,mkdir_cmd)
		rt={}
		exist_cmd='ls  -d %s  '%(db_data_dir)
		exist_flag=sys_cmd(db_host,exist_cmd)
		print exist_flag
		if exist_flag['status']==-1:
			exist_flag=False
		else:
			exist_flag=True
		if not exist_flag:
		    rt['status']=-1
		    rt['info']='mkdir failed'
		    return rt
		chown_datadir_cmd='chown -R %s.%s %s'%(db_user,db_group,db_data_dir)
		chown_datadir_rt=sys_cmd(db_host,chown_datadir_cmd)
		get_mysql_data='scp -r /data/db/mysql/mysql-%s/*  %s:%s'%(db_version,db_host,db_data_dir)
		temp_rt=run_command(get_mysql_data)
		if db_port!=3306:
			mv_config_name='mv %s/my3306.cnf %s/my%s.cnf'%(db_data_dir,db_data_dir,str(db_port))
			temp_rt=sys_cmd(db_host,mv_config_name)
		config_file='%s/my%s.cnf'%(db_data_dir,str(db_port))
		binlog_index='%s/mysqllog/mysql-bin.index'%(db_data_dir)
		replace_port_cmd='sed -i "s#3306#%s#g" %s'%(str(db_port),config_file)
		replace_port_rt=sys_cmd(db_host,replace_port_cmd)
		replace_binlogindex_cmd='sed -i "s#3306#%s#g" %s'%(str(db_port),binlog_index)
		replace_binlogindex_rt=sys_cmd(db_host,replace_binlogindex_cmd)
		replace_port_cmd='sed -i "s#/data#/%s#g" %s'%(opts.datadir,config_file)
		replace_port_rt=sys_cmd(db_host,replace_port_cmd)
		config = NewRawConfigParser(allow_no_value=True,new_option_len=33)
		config.read(config_file)
		socket_path='%s/my%s.sock'%(db_data_dir,str(db_port))
		get_ip_cmd="/sbin/ifconfig |grep inet|cut -f2 -d:|cut -f1 -d ' '|sort -nr|grep -v '127.0.0.1'|head -n 1"
		ip_addr=sys_cmd(db_host,get_ip_cmd)['result'].strip()
		if len(ip_addr)==0:
		    rt['status']=-1
		    rt['info']='Get IP failed'
		    return rt
		ip_addr=ip_addr.split('.')
		server_id='%s%s%s'%(str(ip_addr[2]),str(ip_addr[3]),str(db_port))
		t_rep_cmd="\"sed -i -r 's#(datadir).*#\\1 = %s#g' %s\""%(data_base_dir,config_file)
		sys_cmd(db_host,t_rep_cmd)
		t_rep_cmd="\"sed -i -r 's#(innodb_buffer_pool_size).*#\\1 = %s#g' %s\""%(db_buffer,config_file)
		sys_cmd(db_host,t_rep_cmd)
		t_rep_cmd="\"sed -i -r 's#(server-id).*#\\1 = %s#g' %s\""%(str(server_id),config_file)
		sys_cmd(db_host,t_rep_cmd)
		
		if db_role == 'slave':
			t_rep_cmd="\"sed -i -r 's/(read_only).*/\\1 = %s/g' %s\""%('1',config_file)
			sys_cmd(db_host,t_rep_cmd)
		rt['status']=0
		rt['info']='MySQL Install Success!'
		return rt
		
	else:
		mkdir_cmd='mkdir -p %s'%(db_data_dir)
		temp_rt=run_command(mkdir_cmd)
		rt={}
		if not os.path.exists(db_data_dir):
		    rt['status']=-1
		    rt['info']='mkdir failed'
		    return rt
		chown_datadir_cmd='chown -R %s.%s %s'%(db_user,db_group,db_data_dir)
		chown_datadir_rt=run_command(chown_datadir_cmd)
		get_mysql_data='cp -r  /data/db/mysql/mysql-%s/*  %s'%(db_version,db_data_dir)
		temp_rt=run_command(get_mysql_data)
		if db_port!=3306:
			mv_config_name='mv %s/my3306.cnf %s/my%s.cnf'%(db_data_dir,db_data_dir,str(db_port))
			temp_rt=run_command(mv_config_name)
		config_file='%s/my%s.cnf'%(db_data_dir,str(db_port))
		binlog_index='%s/mysqllog/mysql-bin.index'%(db_data_dir)
		replace_port_cmd='sed -i "s#3306#%s#g" %s'%(str(db_port),config_file)
		replace_port_rt=run_command(replace_port_cmd)
		replace_binlogindex_cmd='sed -i "s#3306#%s#g" %s'%(str(db_port),binlog_index)
		replace_binlogindex_rt=run_command(replace_binlogindex_cmd)
		replace_port_cmd='sed -i "s#/data#/%s#g" %s'%(opts.datadir,config_file)
		replace_port_rt=run_command(replace_port_cmd)
		config = NewRawConfigParser(allow_no_value=True,new_option_len=33)
		config.read(config_file)
		socket_path='%s/my%s.sock'%(db_data_dir,str(db_port))
		get_ip_cmd="/sbin/ifconfig |grep inet|cut -f2 -d:|cut -f1 -d ' '|sort -nr|grep -v '127.0.0.1'|head -n 1"
		ip_addr=run_command(get_ip_cmd)[0].strip()
		if len(ip_addr)==0:
		    rt['status']=-1
		    rt['info']='Get IP failed'
		    return rt
		ip_addr=ip_addr.split('.')
		server_id='%s%s%s'%(str(ip_addr[2]),str(ip_addr[3]),str(db_port))
		config.set("mysqld","datadir",data_base_dir)
		#config.set("mysqld","socket",socket_path)
		config.set("mysqld","innodb_buffer_pool_size",db_buffer)
		config.set("mysqld","server-id",server_id)
		
		if db_role == 'slave':
			config.set("mysqld","read_only",1)
		with open(config_file,'wb') as configfile:
		    config.write(configfile)
		rt['status']=0
		rt['info']='MySQL Install Success!'
		return rt
    else:
        rt['status']=0
        rt['info']='MySQL Port is exists!'
        return rt

	
print main()
