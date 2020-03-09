#!/usr/bin/env python2.7
#coding=utf-8

import json
import urllib2
import sys
import sys,argparse
class zabbixtools:
    def __init__(self):
        #self.url = "http://10.110.18.203:8360/api_jsonrpc.php"
        self.url = "http://10.130.0.64/api_jsonrpc.php"
        self.header = {"Content-Type": "application/json"}
        self.authID = self.user_login()
    def user_login(self):
        data = json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "user.login",
                    "params": {
                        "user": "Admin",
                        "password": "9vIwjVCvlwF2C9zr"
                        },
                    "id": 0
                    })
        request = urllib2.Request(self.url,data)
        for key in self.header:
            request.add_header(key,self.header[key])
        try:
            result = urllib2.urlopen(request)
        except URLError as e:
            print "Auth Failed, Please Check Your Name And Password:",e.code
        else:
            response = json.loads(result.read())
            result.close()
            authID = response['result']
            return authID
    def get_data(self,data,hostip=""):
        request = urllib2.Request(self.url,data)
        for key in self.header:
            request.add_header(key,self.header[key])
        try:
            result = urllib2.urlopen(request)
        except URLError as e:
            if hasattr(e, 'reason'):
                print 'We failed to reach a server.'
                print 'Reason: ', e.reason
            elif hasattr(e, 'code'):
                print 'The server could not fulfill the request.'
                print 'Error code: ', e.code
            return 0
        else:
            response = json.loads(result.read())
            result.close()
            return response
    def hostgroup_get(self):
        data = json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "hostgroup.get",
                    "params": {
                        "output": "extend",
                        },
                    "auth": self.authID,
                    "id": 1,
                    })
        res = self.get_data(data)
        if 'result' in res.keys():
            res = res['result']
            if (res !=0) or (len(res) != 0):
                print "\033[1;32;40m%s\033[0m" % "Number Of Group: ", "\033[1;31;40m%d\033[0m" % len(res)
                for host in res:
                    print "\t","HostGroup_id:",host['groupid'],"\t","HostGroup_Name:",host['name'].encode('GBK')
                print
        else:
            print "Get HostGroup Error,please check !"
    def hostgroup_create(self,hostgroupName=''):
	if self.hostgroup_exist(hostgroupName):
		#print " hostgroupName "+hostgroupName+" is exit"
		return self.hostgroup_exist(hostgroupName)
	if hostgroupName.strip() == '':
		print "hostgroup_create hostgroupName  is null"
		sys.exit()
        data = json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "hostgroup.create",
                    "params": {
                        "name": hostgroupName,
                        },
                    "auth": self.authID,
                    "id": 1,
                    })
        res = self.get_data(data)
	#print res
	if len(res["result"]) !=0:
		print " hostgroup_create "+hostgroupName +" sucess "
		return res["result"]["groupids"][0]
	else:
		return 0


    def hostgroup_exist(self,hostgroupName=''):
	if hostgroupName.strip() == '':
		print "hostgroup_exist hostgroupName  is null"
		sys.exit()
        data = json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "hostgroup.get",
                    "params": {
			"output": "extend",
		        "filter": {
            		   "name": [
                		hostgroupName
            		   ]
        		}
                     },
                    "auth": self.authID,
                    "id": 1,
                    })
        res = self.get_data(data)
	if len(res["result"]) !=0:
		if  res["result"][0]["name"].strip()== hostgroupName:
			#print res["result"][0]["groupid"]
			return res["result"][0]["groupid"]
		else:
			return 0
	else:
		return 0

    def template_get(self,templateName=''):
	if templateName.strip() == '':
		print "template_get templateName=''  is null"
		sys.exit()
        data = json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "template.get",
                    "params": {
			"output": "extend",
		        "filter": {
            		   "name": [
                		templateName
            		   ]
        		}
                     },
                    "auth": self.authID,
                    "id": 1,
                    })
        res = self.get_data(data)

	if len(res["result"]) !=0:
		if  res["result"][0]["host"].strip()== templateName:
			#print res["result"][0]["host"]
			#print res["result"][0]["templateid"]
			return res["result"][0]["templateid"]
		else:
			return 0
	else:
		print "templateName: " +templateName +" is not exit"
		return 0

    def auto_Registration_exit(self,autoRegistrationName=''):
	if autoRegistrationName.strip() == '':
		print " auto_Registration_exit autoRegistrationName is null"
		sys.exit()
        data = json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "action.get",
                    "params": {
			"output": "extend",
		        "filter": {
            		   "name": [
                		autoRegistrationName
            		   ]
        		}
                     },
                    "auth": self.authID,
                    "id": 1,
                    })
        res = self.get_data(data)
	#print res
	if len(res["result"]) !=0:
		if  res["result"][0]["name"].strip()== autoRegistrationName:
			#print res["result"][0]["actionid"]
			return res["result"][0]["actionid"]
		else:
			return 0
	else:
		return 0

    def auto_Registration(self,autoRegistrationName='',hostname="",metadata="",templateid='',groupid=""):
	if autoRegistrationName.strip() == '':
		print "Auto_Registration autoRegistrationName  is null"
		sys.exit()
	if self.auto_Registration_exit(autoRegistrationName):
		#print "autoRegistrationName:" + autoRegistrationName +" is exit"
		return 0
	if templateid.strip() == '':
		print "Auto_Registration templateid  is null"
		sys.exit()
	if groupid.strip() == '':
		print "Auto_Registration groupid  is null"
		sys.exit()
        data = json.dumps(
                {
		    "jsonrpc": "2.0",
		    "method": "action.create",
		    "params": {
		        "name": autoRegistrationName,
		        "eventsource": 2,
		        "status": 0,
		        "esc_period": 0,
		        "filter": {
		            "evaltype": 1,
		            "conditions": [
		                {
		                    "conditiontype": 22,
				    "operator":"2",
		                    "value": hostname
		                },
		                {
		                    "conditiontype": 24,
				    "operator":"2",
		                    "value": "Linux",
		                },
		                {
		                    "conditiontype": 24,
				    "operator":"2",
		                    "value": metadata
		                }
		            ]
		        },
		        "operations": [
		            {
		                "optemplate": [
		                    {
		                        "templateid": templateid
		                    }
		                ],
		                "operationtype": 6,
		            },
		            {
		                "opgroup": [
		                    {
		                        "groupid": groupid
		                    }
		                ],
		                "operationtype": 4,
		            },
		        ]
		    },
		    "auth": self.authID,
		    "id": 1
		}
		)
        res = self.get_data(data)

	if len(res["result"]) !=0:
		#print res["result"]["actionids"][0]
		return res["result"]["actionids"][0]
	else:
		return 0



#test=zabbixtools()
#groupid=test.hostgroup_create("test_test3")
#templateid=test.template_get("Template OS Linux dev")
#print templateid
#test.auto_Registration("test","hostname","md5sum",templateid,groupid)

if __name__ == "__main__":
	zabbix=zabbixtools()
	parser=argparse.ArgumentParser(description='zabbix  api ',usage='%(prog)s [options] example:python  zabbix_login.py  -A test -H hostname_test555 -M md5555 -G group_test11 -T "Template OS Linux dev"')
	parser.add_argument('-A','--autoregname',nargs='?',dest='autoRegistrationName',default='autoRegistrationName',help='创建自动注册的名字')
	parser.add_argument('-H','--hostname',nargs='?',dest='hostname',default='hostname',help='自动注册匹配的主机名')
	parser.add_argument('-M','--metadata',nargs='?',dest='metadata',default='metadata',help='自动注册匹配主机的metadata,例如主机名的md5')
	parser.add_argument('-G','--hostgroupname',nargs='?',dest='hostGroupName',default='hostGroupName',help='自动注册添加的用户组')
	parser.add_argument('-T','--template',nargs='?',dest='template',default='template',help='自动注册添加的模板')
	parser.add_argument('-v','--version', action='version', version='%(prog)s 1.0')
	if len(sys.argv)==1:
		print parser.print_help()
	else:
		args=parser.parse_args()
		#print args.autoRegistrationName
		#print args.hostname
		#print args.metadata
		#print args.hostGroupName
		#print args.template
	        #if args.autoRegistrationName != 'host' :
	       	#	print "sss"
                if args.autoRegistrationName == "autoRegistrationName":
	        	print  "autoRegistrationName is not set"
			print parser.print_help()

                if args.hostname == "hostname":
			print 	" hostname is not set"
			print parser.print_help()

                if args.metadata == "metadata":
			print 	"metadata is not set"
			print parser.print_help()

		if args.hostGroupName == "hostGroupName":
			print 	"hostgroupname is not set"
			print parser.print_help()

		if args.template == "template":
			print 	"template is not set"
			print parser.print_help()
		args.autoRegistrationName=args.autoRegistrationName.strip()
		args.hostname=args.hostname.strip()
		args.metadata=args.metadata.strip()
		args.hostGroupName=args.hostGroupName.strip()
		#print args.template
		#args.template=args.template().strip()


	groupid=zabbix.hostgroup_create(args.hostGroupName)
	#print groupid
	templateid=zabbix.template_get(args.template)
	if templateid == 0:
		print "template:\""+args.template +"\" is not exit"
		sys.exit()
	actionid=zabbix.auto_Registration(args.autoRegistrationName,args.hostname,args.metadata,templateid,groupid)
	if actionid != 0:
		print "actionid: "+str(actionid)
		print "autoRegistrationName: "+args.autoRegistrationName+" is created sucessfully"
	#else:
	    #print "autoRegistrationName: "+args.autoRegistrationName+" is exsit"
