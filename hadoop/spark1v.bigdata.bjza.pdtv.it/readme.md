

###配置ambari yum源
ansible-playbook  -i add  -e "hosts=add" yum-deploy.yaml -k -K -s

##作用ssh key部署,无秘钥访问目标机。

#root账号
ansible-playbook -i   /tmp/2.txt    -e "hosts=add"  -e "user=root"  -e "hostname=ambari1v.ops.soho.pdtv.it"  -e "baktime=201702161104"  rootsshkey.yaml -k -K -s -u liqingbin

##部署hosts文件
ansible-playbook  -i add -e "hosts=add" -e "version=201703221642" hosts-deploy.yaml  -k -K -s -uliqingbin
