##作用ssh key部署,无秘钥访问目标机。

需要登切换到root 账号下面执行下面的命令

##例子

                                机器列表                       发布的机器组或者单个机器      指定ssh key用户           当前主机名               备份原来版本的时间戳                        执行ansible 用户
ansible-playbook -i   /home/q/tools/game_team/svr/ansible.yml   -e "hosts=bjac_main_dd"  -e "user=search"  -e "hostname=dev03.pandatv.com"  -e "baktime=201612261053"  sshkey.yaml -k -K -s -u liqingbin



#root账号
ansible-playbook -i   /tmp/2.txt    -e "hosts=add"  -e "user=root"  -e "hostname=ambari1v.ops.soho.pdtv.it"  -e "baktime=201702161104"  rootsshkey.yaml -k -K -s -u liqingbin
