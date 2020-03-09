作用：把centos7 的防火墙改为iptables 并设置默认防火墙规则

#例子
                      机器列表         发版机器
ansible-playbook -i   txhosts   -e "hosts=sht-t"  iptables7.yaml  -k -K -s
