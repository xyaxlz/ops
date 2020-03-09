
#主要在腾讯机房
作用：把centos7 的防火墙改为iptables 并设置默认防火墙规则

#例子
                      机器列表         发版机器
ansible-playbook -i   txhosts   -e "hosts=sht-t"  iptables7.yaml  -k -K -s



## 配置特殊iptables
 ansible -i txhosts all  -m copy -a "src=iptables_rules/030.host.default dest=/usr/local/etc/iptables_rules/" -k -K -s

 ansible -i txhosts all  -m  service -a "name=iptables state=restarted" -k -K -s
