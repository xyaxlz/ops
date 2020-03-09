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
import socket
import redis
import traceback

sys.path.append('/etc/db_tools')
from mysqllib import *
from syslib import *
admin_user='db_admin'
admin_passwd='BZs*gIyVeH4o0q!f'
admin_port=3307
admin_host='127.0.0.1'
admin_hostname='mha1v.infra.bjac.pdtv.it'
import warnings
warnings.filterwarnings("ignore", category = MySQLdb.Warning)
def get_redis_pass(host,port):
	try:
		get_pass_cmd='cat /etc/redis/%s.conf|grep ^requirepass'%(str(port))	
		rt=sys_cmd(host,get_pass_cmd)
		if rt['status']==-1:
			return rt
		if len(rt['result'])>0:
			password=rt['result'].split()[-1]
			rt['result']=password
		return rt
	except Exception,e:
		print traceback.print_exc()
def get_redis_password(hostname,port):
    try:
	conn=MySQLBase(admin_host,admin_port,admin_user,admin_passwd)
        sql="select port,password  from panda_db_admin.redis_auth where port=%d;"%(int(port))
        sql_rt=conn.query(sql)
        rt={}
        if len(sql_rt)==0:
                password=get_redis_pass(hostname,port)
                if password['status']==-1:
                    return password
                password=password['result']
                if len(password)==0:
                    rt['status']=0
                    rt['result']=''
                    sql="replace into panda_db_admin.redis_auth (port,password) values(%d,'%s');"%(int(port),password)
                    sql_rt=conn.query(sql)
                    rt['status']=0
                    rt['result']=password[0]['password']
                    return rt
                else:
                    sql="insert into panda_db_admin.redis_auth (port,password) values(%d,'%s');"%(int(port),password)
                    sql_rt=conn.query(sql)
                    rt['status']=0
                    rt['result']=password
                    return rt
        else:
	    rt['status']=0
	    rt['result']=sql_rt[0]['password']
            return rt
    except Exception,e:
        print traceback.print_exc()




def arg_parse():

    parse = argparse.ArgumentParser(description='Redis Login')
    parse.add_argument('--port', '-P', type=int,default=0,
                       help='redis port')
    parse.add_argument('--host', '-H', default=0,help='redis host')
    parse.add_argument('--hostname', '-n', default='',help='redis hostname')
    parse.add_argument('--dc', '-d', default='',help='redis idc')
    parse.add_argument('--cmd', '-c', default='',help='redis command')
    return parse, parse.parse_args()
def redis_login(host,port,password,cmd):
    try:
    	if len(cmd)==0:
		if password:
			redis_cmd="/usr/local/redis-3.2/bin/redis-cli -p  %s -a %s -h %s %s"	%(str(port),password,host,cmd)
		else:
			redis_cmd="/usr/local/redis-3.2/bin/redis-cli -p  %s  -h %s %s"	%(str(port),host,cmd)
		p=subprocess.Popen(redis_cmd,shell=True)
                stdout,stderr = p.communicate()
                retcode = p.wait()

	else:
		
		redis_cmd="/usr/local/redis-3.2/bin/redis-cli -p  %s -a %s -h %s %s"	%(str(port),password,host,cmd)
		rt=cmd_exec(redis_cmd)
		return rt
    except Exception,e:
        print traceback.print_exc()

def main():
    try:
	    parser, opts = arg_parse()
	    args_len=len(sys.argv)
	    host=opts.host
	    port=opts.port
	    hostname=opts.hostname
	    cmd=opts.cmd
    	    dc=opts.dc
	    if not host:
	        cur_hostname=socket.gethostname()
	    	if cur_hostname!=admin_hostname:
            		host='127.0.0.1'
		if not port:
            		host='127.0.0.1'
			
	    if int(port)>0 and dc in ['ac','za'] and int(host)>0:
	    	hostname="rdb%sv.infra.bj%s.pdtv.it"%(str(host),dc)
	        password=get_redis_password(hostname,port)
	    	rt=redis_login(hostname,port,password,cmd)	
	    if  dc in ['ac','za'] and len(hostname)>0:
	    	hostname="%sv.infra.bj%s.pdtv.it"%(str(hostname),dc)
	    try:
		    if  dc in ['ac','za'] and int(host)>0:
			hostname="rdb%sv.infra.bj%s.pdtv.it"%(str(host),dc)
	    except Exception,e:
	    	    print
	    #if port==0 and len(host)==0:
            #	rt={}
	    #	rt['status']=-1
            #		rt['result']='Host Port Failed'
	    #	return rt
	    if port==0:
		    if host!='':
			    if check_ip(host):
				host=host
			    elif re.match(r'[0-9]+',host):
				rt={}
				if len(dc)==0:
					rt['status']=-1
					rt['result']='No idc info!'
					return rt
				if  dc not in ['ac','za']:
					rt['status']=-1
					rt['result']='idc not exists!'
					return rt
				host="rdb%sv.infra.bj%s.pdtv.it"%(str(host),dc)
			    else:
				rt={}
				rt['status']=-1
				rt['result']='IP is not Valid'
				return rt
		    conn=MySQLBase(admin_host,admin_port,admin_user,admin_passwd)
		    if host!='127.0.0.1' or  len(hostname)>0:
		    	    if len(hostname)==0 and check_ip(host):
				sql="select port,case master when length(master)=0 then 'slave' when length(master)>0 then 'master' end as role,prod_info from cmdb.redis_ins where ip='%s';"%(host)
			    else:
				sql="select port,case master when length(master)=0 then 'slave' when length(master)>0 then 'master' end as role,prod_info from cmdb.redis_ins where hostname='%s';"%(hostname)
			    sql_rt=conn.query(sql)
			    if len(sql_rt)==0:
				rt={}	
				rt['status']=-1
				rt['result']='No Redis Instance'
				return rt
			    else:
				port_info='\033[1;31;40m%s\n%s\t %5s \t %5s\t %10s\n'%('Port Info:','ID','Port','Role','Product')
				for i in sql_rt:
					if i['role']=='master':
						color_info="\033[1;31;40m"
					else:
						color_info="\033[1;36;40m"
					port_info='%s%s%d\t %5s \t %5s    %5s\n'%(port_info,color_info,sql_rt.index(i)+1,str(i['port']),i['role'],i['prod_info'].strip())
		    else:
			    ports=[]
		            get_port="ps aux|grep redis|grep -v grep|grep -v python|grep -v zabbix" 		
			    p=subprocess.Popen(get_port,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
                            stdout,stderr = p.communicate()
		            port_info='\033[1;31;40m%s\n%s\t %5s\n'%('Port Info:','ID','Port')
			    if not stdout:
			        rt={}
				rt['status']=0
                                rt['result']='No Redis Port'
                                return rt
                            port_list=stdout.split('\n')
	                    for i in port_list:
			        if len(i)>0:
					j=i
					i=i.split()
					color_info="\033[1;36;40m"
					i=i[-1].split(':')
					i_port=i[1]
					ports.append(i_port)
					port_info="%s%s%d\t %5s\n"%(port_info,color_info,port_list.index(j)+1,i_port)	
                    port_info="%s\033[0m"%port_info
		    print port_info
		    port_idx=0
		    port_idx=raw_input('Please Select Port("ID"):\n')
		    if host!='127.0.0.1' or len(hostname)>0:
		    	port=sql_rt[int(port_idx)-1]['port']
		    else:
		    	port=ports[int(port_idx)-1]
	    if host==0:
		    conn=MySQLBase(admin_host,admin_port,admin_user,admin_passwd)
                    sql="select hostname,case master when length(master)=0 then 'slave' when length(master)>0 then 'master' end as role,prod_info from cmdb.redis_ins where port=%d;"%(int(port))
                    sql_rt=conn.query(sql)
		    if len(sql_rt)==0:
			rt={}	
			rt['status']=-1
			rt['result']='No Redis Instance'
			return rt
		    else:
			port_info='\033[1;31;40m%s\n%s\t %15s \t %15s \t %10s\t %10s\n'%('Host Info:','ID','Host','IP','Role','Product')
			for i in sql_rt:
				if i['role']=='master':
					color_info="\033[1;31;40m"
				else:
					color_info="\033[1;36;40m"
				port_info='%s%s%d\t %5s \t %10s \t %10s    %10s\n'%(port_info,color_info,sql_rt.index(i)+1,str(i['hostname']),socket.gethostbyname(i['hostname']),i['role'],i['prod_info'].strip())
                    port_info="%s\033[0m"%port_info
		    print port_info
		    port_idx=0
		    port_idx=raw_input('Please Select Host("ID"):\n')
		    host=sql_rt[int(port_idx)-1]['hostname']
	    if host!='127.0.0.1' or  len(hostname)>0: 	
	        password=get_redis_password(host,port)
	    else:
	        password=get_redis_pass(host,port)
	    if password['status']!=0:
		return password
	    password=password['result']
	    
	    if len(cmd)==0 or cmd=="monitor":
		if len(hostname)>0:
	    		redis_login(hostname,port,password,cmd)	
		else:
	    		redis_login(host,port,password,cmd)	
	    else:
		if len(hostname)>0:
	    		rt=redis_login(hostname,port,password,cmd)	
		else:
	    		rt=redis_login(host,port,password,cmd)	
		return rt['result']
			

    except Exception,e:
        print traceback.print_exc()
print main()
