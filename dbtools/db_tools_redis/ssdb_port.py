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
from  ssdb import connection
import subprocess
import socket
sys.path.append('/etc/db_tools')
from mysqllib import *
from syslib import *
from config_set  import *

db_user = 'superdba'
db_passwd = '5CHcQzFhIbVaTHzL'
admin_user='db_admin'
admin_passwd='BZs*gIyVeH4o0q!f'
admin_port=3307
admin_host='127.0.0.1'


def arg_parse():
    try:
        parse = argparse.ArgumentParser(description='SSDB Port')
        parse.add_argument('--port', '-P', type=int, required=True, help='ssdb port')
        options = parse.parse_args()
        return parse, options
    except Exception, e:
        print e

def ssdb_info(host,port):
	ssdb=connection.Connection(host=host,port=port)
	ssdb.send_command('info')
	rt=ssdb.read_response()
	return rt

def get_master(port):
	my_conn=MySQLBase(admin_host,admin_port,admin_user,admin_passwd)
	sql="select hostname  from cmdb.ssdb_ins where port=%d and master='';"%(int(port))
	rt=my_conn.query(sql)
	return rt
def main():
	 parse, opts = arg_parse()
	 port=opts.port
	 #print port
	 rt={}
	 master_host=get_master(port) 
	 if len(master_host)==0:
		rt['status']=-1
		rt['result']='No Master'
		return rt
	 master_host=master_host[0]['hostname']
	 info_rt=ssdb_info(master_host,port)
	 master_ip=socket.gethostbyname(master_host)
	 print "\033[1;31;40m  %s"%(master_ip)
	 cur_master_pos=0
	 for i in info_rt:
	 	if re.match(r'repl_client.*',i):
			a=i.split(':')[1].split(',')
			if a[2].split('=')[1]=='mirror':
				t_str="\033[1;33;40m\t\t%10s(%s,%s,%d)"%(a[0].split('=')[1],a[2].split('=')[1],a[3].split('=')[1],int(cur_master_pos)-int(a[4].split('=')[1]))
				print t_str
	 			info1_rt=ssdb_info(a[0].split('=')[1],port)
				for j in info1_rt:	
			 		if re.match(r'repl_client.*',j):
						b=j.split(':')[1].split(',')
						if b[2].split('=')[1]=='mirror':
							t_str="\033[1;33;40m\t\t\t%10s(%s,%s,%d)"%(b[0].split('=')[1],b[2].split('=')[1],b[3].split('=')[1],int(cur1_master_pos)-int(b[4].split('=')[1]))
							print t_str
						else:
							t_str="\033[1;36;40m\t\t\t%10s(%s,%s,%d)"%(b[0].split('=')[1],b[2].split('=')[1],b[3].split('=')[1],int(cur1_master_pos)-int(b[4].split('=')[1]))
							print t_str
					if re.search(r'.*binlog_max_seq.*',j):
						cur1_master_pos=j.split(':')[-1]
							
			else:
				t_str="\033[1;36;40m\t\t%10s(%s,%s,%d)"%(a[0].split('=')[1],a[2].split('=')[1],a[3].split('=')[1],int(cur_master_pos)-int(a[4].split('=')[1]))
				print t_str
		if re.search(r'.*binlog_max_seq.*',i):
			cur_master_pos=i.split(':')[-1]
         print "\033[0m"
main()
