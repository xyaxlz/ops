ansible -i ansible.yml  bjac_main_ruc -m shell -a "cd /home/server_config/rsync;echo y| sh init.sh  install" -k -K -s

ansible-playbook  -i /home/q/tools/game_team/svr/ansible.yml  -e "hosts=bjac_main_ruc" rsyncd.yaml  -k -K -s

ansible -i /home/q/tools/game_team/svr/ansible.yml bjac_main_ruc  -m shell -a "mkdir -p  /home/q/cmstpl/ " -k -K -s

 /usr/bin/rsync -arv   --password-file=/tmp/mi  /home/q/cmstpl/*   cms@10.131.1.14::cms

/usr/bin/rsync -arv   --password-file=/tmp/mi2  /home/q/data/breeder/online/pandaren/*   panda@10.131.1.16::panda
