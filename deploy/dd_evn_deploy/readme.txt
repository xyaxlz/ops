###dd 环境依赖jdk 发版之前把jdk1.7.0_80.tar.gz 解压到当前目录
wget http://10.110.17.7:8888/java/jdk1.7.0_80.tar.gz
tar xvf jdk1.7.0_80.tar.gz

## 新机器环境初始化
ansible-playbook -i   /home/q/tools/game_team/svr/ansible.yml   -e "hosts=bjac_main_dd" dd_evn_deploy.yaml -k -K -s
