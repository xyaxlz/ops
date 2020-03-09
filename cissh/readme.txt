##配置 所需要的系统环境设置


###发版机 执行jumperssh.yaml
ansible-playbook  -i addd    ci.yaml  -e 'hosts=all' -k -K -s -e 'baktime=201702211122'


ansible-playbook  -i ../../ops/ansible.yml  -e "hosts=bjza_plat_t" -e "baktime=201708251848" ci.yaml -k -K -s
