for i in 10
do 
	echo $i
scp zabbix_agent.install  mdb${i}v.infra.bjac.pdtv.it:/tmp/
ssh mdb${i}v.infra.bjac.pdtv.it "cd /tmp/;sh zabbix_agent.install"
scp mongodb.conf  mdb${i}v.infra.bjac.pdtv.it:/etc/zabbix/zabbix_agentd.d/
#a=`ssh -n  mdb${i}v.infra.bjac.pdtv.it 'awk  "/port:/{print $1}" /etc/mongod.conf'|awk '{print $2}'`
#a=`ssh -n  mdb${i}v.infra.bjac.pdtv.it 'awk  "/port:/{print $1}" /etc/mongod.conf'`
a=`ssh -n  mdb${i}v.infra.bjac.pdtv.it  'cd  /data/mongodb/;ls -d * |tail -n 1'`
echo $a
ssh mdb${i}v.infra.bjac.pdtv.it "sed -i 's/7090/$a/g' /etc/zabbix/zabbix_agentd.d/mongodb.conf   "
ssh mdb${i}v.infra.bjac.pdtv.it "/etc/init.d/zabbix-agent restart"
done
