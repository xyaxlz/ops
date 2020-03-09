 ansible-playbook  -i add  -e "hosts=all" rsyncd.yaml  -k -K -s





 /usr/bin/rsync -arv   --password-file=/tmp/mi  /home/q/cmstpl/*   cms@10.131.1.14::cms

/usr/bin/rsync -arv   --password-file=/tmp/mi2  /home/q/data/breeder/online/pandaren/*   panda@10.131.1.16::panda
