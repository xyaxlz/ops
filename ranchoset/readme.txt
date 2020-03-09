##配置rancho 所需要的系统环境设置


###发版机rancho1v 执行rachoset.yaml 文件 例子 ranchohost为机器列表
ansible-playbook  -i ranchohost    ranchoset.yaml  -e 'hosts=all' -k -K -s -e 'baktime=201702211122'


ansible-playbook  -i ranchohost    ranchoset.yaml  -e 'hosts=bjac_plat_t' -k -K -s -e 'baktime=201702211545'

ansible-playbook  -i add   ranchoset.yaml  -e 'hosts=add' -k -K -s -e 'baktime=201702241156'
ansible-playbook  -i add   goranchoset.yaml  -e 'hosts=add' -k -K -s -e 'baktime=201702241156'

###发版机dev09 执行t_ranchoset.yaml 文件
ansible-playbook  -i ranchohost    t_ranchoset.yaml  -e 'hosts=soho_dev' -k -K -s -e 'baktime=201702211545'
ansible-playbook  -i ranchohost    t_goranchoset.yaml  -e 'hosts=soho_dev' -k -K -s -e 'baktime=201702211545'

ansible-playbook  -i add    t_ranchoset.yaml  -e 'hosts=add' -k -K -s -e 'baktime=201702211545'
