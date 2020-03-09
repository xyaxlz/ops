for i in `seq 28`
do
	#ssh-copy-id -i  id_rsa.pub  db${i}v.infra.bjac.pdtv.it
	scp mha4mysql-node-0.57-0.el7.noarch.rpm    db${i}v.infra.bjac.pdtv.it:/data/install
	ssh db${i}v.infra.bjac.pdtv.it "cd /data/install;yum install perl-DBD-MySQL -y;rpm -ivh mha4mysql-node-0.57-0.el7.noarch.rpm"
done
