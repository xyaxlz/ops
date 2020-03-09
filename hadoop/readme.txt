 ansible-playbook  -i lsghostlist  -e "hosts=all" -e "hostsconf=lsghostsconf" hosts-deploy.yaml -k -K -s  -e "version=201701061704"
