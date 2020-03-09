#/bin/bash
version=$1
hosts=$2

rm -rf dd.panda.tv.flume
rm -rf dd.panda.tv.flume_$version

#test -L dd.panda.tv.flume && unlink dd.panda.tv.flume
git clone -b  $version  git@git.pandatv.com:bigdata/dd.panda.tv.flume.git
if [ $? != 0 ];then
    echo "clone err"
    exit

fi
#test -d dd.panda.tv.flume_$version && rm -rf dd.panda.tv.flume_$version
mv dd.panda.tv.flume dd.panda.tv.flume_$version
#ln -s dd.panda.tv.flume_$version dd.panda.tv.flume
ln -s dd.panda.tv.flume_$version  dd.panda.tv.flume
#sudo /home/q/tools/game_team/svr/updatesvr -a
ansible-playbook -i   /home/q/tools/game_team/svr/ansible.yml   -e "hosts=$hosts"  dd_code_deploy.yaml  -f 20  -k -K -s
#ansible-playbook -i ddhosts   -e "hosts=$hosts"  dd_code_deploy.yaml  -f 1  -k -K -s
#ansible-playbook -i add   -e "hosts=$hosts"  dd_code_deploy.yaml  -f 1  -k -K -s


