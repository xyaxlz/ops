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

def arg_parse():

    parse = argparse.ArgumentParser(description='Redis Login')
    parse.add_argument('--port', '-P', type=int, required=True,
                       help='redis port')
    parse.add_argument('--host', '-H', default='',help='redis host')
    parse.add_argument('--dc', '-d', default='',help='redis idc')
    parse.add_argument('--count', '-c', default=20,help='redis count')
    parse.add_argument('--interval', '-i', default=1,help='redis count')
    return parse, parse.parse_args()
def redis_stat(host,port,password,interval,count):
    try:
        redis_cmd="redis-stat  -a %s  %s:%s  %s %s "	%(password,host,port,str(interval),str(count))
        p=subprocess.Popen(redis_cmd,shell=True)
        stdout,stderr = p.communicate()
        retcode = p.wait()
    except Exception,e:
        print traceback.print_exc()

def main():
    try:
        parser, opts = arg_parse()
        args_len=len(sys.argv)
        host=opts.host
        port=opts.port
        count=opts.count
        dc=opts.dc
        interval=opts.interval
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
           # print host,port,cmd,dc
        password=get_redis_pass(host,port)
        if password['status']==-1:
            return password
        password=password['result']
        redis_stat(host,port,password,interval,count)	
    except Exception,e:
        print traceback.print_exc()
print main()
