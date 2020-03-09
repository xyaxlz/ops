#!/usr/bin/env /usr/bin/python2.6
import os
import json
#import simplejson as json  
t=os.popen(""" netstat -tlpn |grep ssdb-server|grep 0.0.0.0|awk '{print $4}'|awk -F: '{print $2}' """)
ports = []
for port in  t.readlines():
        r = os.path.basename(port.strip())
        ports += [{'{#REDISPORT}':r}]
print json.dumps({'data':ports},sort_keys=True,indent=4,separators=(',',':'))
