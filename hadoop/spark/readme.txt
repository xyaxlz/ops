#http://10.110.17.7/HDP/2.5.3.0/centos7/
#http://10.110.17.7/HDP-UTILS-1.1.0.20/repos/centos7/
#在不是hiver的机器上线执行下面的语句解决 mysql 表索引长度不超过 767 bytes的限制
sed -i  's/ENGINE=InnoDB DEFAULT CHARSET=latin1/ENGINE=InnoDB DEFAULT CHARSET=latin1 ROW_FORMAT=COMPRESSED/' /usr/hdp/2.5.3.0-37/hive2/scripts/metastore/upgrade/mysql/hive-schema-2.1.0.mysql.sql




#ssh key deploy
ansible-playbook  -i sparkhosts -e "hosts=all" sshkey.yaml  -k -K -s

#deploy hosts
ansible-playbook  -i sparkhosts -e "hosts=add" -e "version=201612162106" online-spark-hosts-deploy.yaml  -k -K -s


#deploy yum
ansible-playbook  -i sparkhosts  -e "hosts=add" yum-deploy.yaml  -k -K -s
