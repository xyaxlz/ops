


## selinux
cp -v selinux /etc/selinux/config
## sudo
sudof="/etc/sudoers"
sudoer_opt1='Defaults        logfile=/var/log/sudo.log'
sudoer_opt2='Defaults        !syslog'
sudoer_opt3='Defaults        timestamp_timeout=120'
sudoer_ops4='Defaults        !tty_tickets'
for sudo_opt in "$sudoer_opt1" "$sudoer_opt2" "$sudoer_opt3" "$sudoer_opt4"
do
	grep "^$sudo_opt" $sudof > /dev/null 2>&1
	[ $? -ne 0 ]&& echo "$sudo_opt" >> $sudof
done
## sshd
sshf="/etc/ssh/sshd_config"
for ssh_opt in 'UseDNS no' 'PermitRootLogin no'
do
	grep "^$ssh_opt" $sshf > /dev/null 2>&1
	[ $? -ne 0 ]&& echo "$ssh_opt" >> $sshf
done



for dir in  cache cmstpl data lua php pkgs system tools
do
	mkdir -pv "/home/q/$dir"
	chmod 777 "/home/q/$dir"
done


sed -i 's/^inet_protocols = all/inet_protocols = ipv4/g' /etc/postfix/main.cf

systemctl enable postfix
systemctl restart postfix

grep 'mon@panda.tv' /etc/aliases > /dev/null 2>&1
[ $? -eq 0 ] &&exit 0
echo 'root:echomon@panda.tv' >> /etc/aliases
newaliases
