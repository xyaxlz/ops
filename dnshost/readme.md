
###同时添加 count.pdtv.io villa.pdtv.io badge.pdtv.io relation.pdtv.io api.u.panda.tv  hosts解析
ansible-playbook  -i /home/q/tools/game_team/svr/ansible.yml -e "hosts=bjac_man_w" alldns.yml  -k -K -s -f 20


ansible -i /home/q/tools/game_team/svr/ansible.yml  bjac_main_w  -m shell -a "sed -i '/count.pdtv.io\|villa.pdtv.io\|badge.pdtv.io\|relation.pdtv.io\|api.u.panda.tv/s/^/#/g' /etc/hosts" -k -K -s -f 20
ansible -i /home/q/tools/game_team/svr/ansible.yml  bjac_main_w  -m shell -a "sed -i '/10.110/d' /etc/hosts" -k -K -s -f 20

