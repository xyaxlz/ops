for i in {7,8,9,10,11,12}
do 
	echo $i
#scp redis.conf  rdb${i}v.infra.bjac.pdtv.it:/etc/zabbix/zabbix_agentd.d/
#scp -r scripts/  rdb${i}v.infra.bjac.pdtv.it:/etc/zabbix/
ssh rdb${i}v.infra.bjac.pdtv.it "chmod +s /bin/netstat"
#ssh rdb${i}v.infra.bjac.pdtv.it "yum install python-simplejson -y"
ssh rdb${i}v.infra.bjac.pdtv.it "/etc/init.d/zabbix-agent restart"
done
