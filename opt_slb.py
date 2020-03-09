#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
'''
Created on 2016-7-19
'''
import json, sys, argparse
import aliyun.api, util

reload(sys)
sys.setdefaultencoding("utf-8")

parser = argparse.ArgumentParser(description="opt slb")
parser.add_argument("opt", choices=["add", "del"], help="opt type, add or del")
group1 = parser.add_argument_group("args about add")
group1.add_argument("-r", "--region", help="region: default cn-beijing", default="cn-beijing")
group1.add_argument("--lp", help="listen port", required=True,type=int)
group1.add_argument("--lbn", help="load balancer name", required=True)
group1.add_argument("--at", help="address type, default intranet", choices=["intranet", "internet"],default="intranet")
group1.add_argument("--bw", help="bind with, default -1", default=-1,type=int)
group1.add_argument("--ict", help="internet charge type, default paybytraffic",choices=["paybytraffic","paybybandwidth"],default="paybytraffic")
group1.add_argument("--hcct", help="health check connect timeout, default 2",default=2,type=int)
group1.add_argument("--hci", help="health check interval, default 2",default=2,type=int)
group1.add_argument("--ht", help="health threshold, default 2",default=2,type=int)
group1.add_argument("--uht", help="unhealth threshold, default 2",default=2,type=int)
group1.add_argument("--pt", help="persistence timeout, default 0",default=0,type=int)
group1.add_argument("--sd", help="scheduler type, default wrr",default="wrr")
group1.add_argument("--vpcid", help="vpc id, default vpc-25ojfxcpo",default="vpc-25ojfxcpo",choices=["vpc-25ojfxcpo"])
group1.add_argument("--vsid", help="vswitch id, default vsw-25vuv4yfi",default="vsw-25vuv4yfi",choices=["vsw-25vuv4yfi"])

group2 = parser.add_argument_group("args about del")
ex_group = group2.add_mutually_exclusive_group()
ex_group.add_argument("-a", "--address", help="slb address")
ex_group.add_argument("-l", "--loadbalancerid", help="slb id")
args = parser.parse_args()


def main():
    if args.opt == "add" :
        print "AddressType:",args.at
        print "LoadBalancerName:",args.lbn
        print "ListenerPort:",args.lp
        print "VpcId:",args.vpcid
        print "VSwitchId:",args.vsid
        print "Scheduler:",args.sd
        confirm = raw_input("Are you sure to create slb [y/n]")
        if confirm.lower() != 'y':
            sys.exit(0)

        req = aliyun.api.Slb20140515CreateLoadBalancerRequest()
        req.AddressType = args.at
        req.Bandwidth = args.bw
        req.InternetChargeType = args.ict
        req.LoadBalancerName = args.lbn
        req.RegionId = args.region
        req.VpcId = args.vpcid
        req.VSwitchId = args.vsid
        try:
            f = req.getResponse()
        except Exception:
            print "create load balancer request fail"
            sys.exit(1)

        slbId = f["LoadBalancerId"]
        req2 = aliyun.api.Slb20140515CreateLoadBalancerTCPListenerRequest()
        req2.BackendServerPort = args.lp
        req2.Bandwidth = args.bw
        req2.HealthCheckConnectPort = args.lp
        req2.HealthCheckConnectTimeout = args.hcct
        req2.HealthCheckInterval = args.hci
        req2.HealthyThreshold = args.ht
        req2.ListenerPort = args.lp
        req2.LoadBalancerId = slbId
        req2.PersistenceTimeout = args.pt
        req2.Scheduler = args.sd
        req2.UnhealthyThreshold = args.uht
        try:
            f2 = req2.getResponse()
        except Exception:
            print "create load balancer tcp listener request fail"
            sys.exit(1)

        req3 = aliyun.api.Slb20140515StartLoadBalancerListenerRequest()
        req3.ListenerPort = args.lp
        req3.LoadBalancerId = slbId
        try:
            f3 = req3.getResponse()
        except Exception:
            print "start load balancer listener request fail"
            sys.exit(1)

        print "create load balancer success"
        slbInfo = util.getSlbInfo(slbId, args.region)
        print json.dumps(slbInfo,indent=4)

    elif args.opt == "del":
        '''
        req4 = aliyun.api.Slb20140515StopLoadBalancerListenerRequest()
        req4.ListenerPort = args.lp
        req4.LoadBalancerId = args.loadbalancerid
        try:
            req4.getResponse()
        except Exception:
            print "stop load balancer listener request fail"
            sys.exit(1)
        '''
        req5 = aliyun.api.Slb20140515DeleteLoadBalancerRequest()
        req5.LoadBalancerId = args.loadbalancerid
        try:
            f5 = req5.getResponse()
            print json.dumps(f5,indent=4)
        except Exception:
            print "delete load balancer request fail"
            sys.exit(1)

        print "delete load balancer request success"

if __name__=="__main__":
    main()
