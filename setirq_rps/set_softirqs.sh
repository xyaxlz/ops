#!/bin/bash

set_softirqs()
{
	eth=$1
	cpu=0
	for i in `grep ${eth}-TxRx /proc/interrupts |awk -F":" '{print $1}'`
	do
    		#echo $cpu
   	 	echo $cpu >/proc/irq/$i/smp_affinity_list
    		cat /proc/irq/$i/smp_affinity_list
    	cpu=$(($cpu + 1))
	done
}

set_softirqs eth0
set_softirqs eth1
