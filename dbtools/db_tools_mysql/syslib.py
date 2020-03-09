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

bad_command=['reboot','init','kill']
def sys_cmd(host,cmd):
	try:
		cmd_info='ssh %s %s'%(host,cmd)
		p=subprocess.Popen(cmd_info,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
		stdout,stderr = p.communicate()	
		rt={}
		if len(stderr)==0:
			rt['status']=0
			rt['result']=stdout
		else:
			rt['status']=-1
			rt['result']=stderr
		return rt	
	except Exception,e:
		print traceback.print_exc()
def cmd_exec(cmd):
	try:
		p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
		stdout,stderr = p.communicate()	
	        return_code=p.returncode
		rt={}
		if return_code ==0:
			rt['status']=0
			rt['result']=stdout
		else:
			rt['status']=-1
			rt['result']=stderr
		return rt	
	except Exception,e:
		print traceback.print_exc()


def check_ip(ipaddr):
        import sys
        addr=ipaddr.strip().split('.')  
        if len(addr) != 4:  
		return False
        for i in range(4):
                try:
                        addr[i]=int(addr[i])   
                except:
			return False
                if addr[i]<=255 and addr[i]>=0:  
                        pass
                else:
			return False
                i+=1
        else:
		return True
#a=sys_cmd('10.120.0.249','cat /etc/redis/6099.conf|grep ^requirepass')
#print a
#print a['result'].split()
#print cmd_exec('date')
