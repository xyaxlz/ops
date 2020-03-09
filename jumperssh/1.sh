for i in `cat groups`
do
    echo "######################## $i"
    echo "######################## $i" >> downgroups
    ansible-playbook  -i ../../ops/ansible.yml   -e "hosts=$i" -e "baktime=201709051911" jumperssh.yaml -k -K -s -f 50

done
