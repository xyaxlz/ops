# -*- coding: utf-8 -*-
import os
import paramiko
import time

class Homeq_Copy:
	'''
	从原目标机copy /home/q /usr/loca/nginx/cert /data/darknet/ 数据到目标机器
	'''
	def __init__(self,pkey,src_hostname,src_homeqtar_dir,local_homeqtar_dir):
		self.pkey=pkey
		self.src_hostname=src_hostname
		self.src_homeqtar_dir=src_homeqtar_dir
		self.local_homeqtar_dir=local_homeqtar_dir

	def homeq_tar(self):
		
		key=paramiko.RSAKey.from_private_key_file(self.pkey)
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(self.src_hostname,username = 'rancho',pkey=key)

		stdin,stdout,stderr=ssh.exec_command('find /home/q/  -maxdepth 1 -type d |grep -v /home/q/pkgs |grep -v -w /home/q/')
		qdir_tuple=tuple(stdout.read().split())
		if not qdir_tuple:
			print 'qdir_tuple is null'
		
		stdin,stdout,stderr=ssh.exec_command('find /home/q  -type l -exec ls -l {} \;  |awk -F \'->\'  \'{print $2}\'|grep \'/home/q/pkgs/\'')
		link_tuple=tuple(stdout.read().split())
		if not link_tuple:
			print 'link_tuple is null'
		
		tarfile_tuple=qdir_tuple+link_tuple
		if qdir_tuple and link_tuple and tarfile_tuple:
		
			#tarcmd='sudo tar -czf  '+self.src_homeqtar_dir+' '+' '.join(tarfile_tuple) 
			stdin,stdout,stderr=ssh.exec_command('sudo test -d  /data/darknet/ ')
			if not stdout.channel.recv_exit_status():
				tarcmd="sudo tar -czf {} {}  /usr/local/nginx/conf/certs/ /data/darknet/".format(self.src_homeqtar_dir,' '.join(tarfile_tuple))
			else:
				tarcmd="sudo tar -czf {} {}  /usr/local/nginx/conf/certs/".format(self.src_homeqtar_dir,' '.join(tarfile_tuple))
				
			stdin,stdout,stderr=ssh.exec_command(tarcmd)
			if not stdout.channel.recv_exit_status():
				print 'sudo tar -czf  '+self.src_homeqtar_dir+' '+' '.join(tarfile_tuple)+' DONE'
			ssh.close()
		else:
			print 'sudo tar -czf  '+self.src_homeqtar_dir+' '+' FAIL'
			ssh.close()
			return 0
		print 'homeq_tar {} done'.format(self.src_hostname)
	 
	def homeq_tar_get(self):
		key=paramiko.RSAKey.from_private_key_file(self.pkey)
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(self.src_hostname,username = 'rancho',pkey=key)
	   
		transport = paramiko.Transport((self.src_hostname, 22))
		transport.connect(username='rancho', pkey=key)
		sftp = paramiko.SFTPClient.from_transport(transport)
		sftp.get(self.src_homeqtar_dir,self.local_homeqtar_dir)
		sftp.close()
		ssh.close()
		print 'homeq_tar_get {} done'.format(self.src_hostname)
	
	def homeq_put_untar(self,dest_hostname):
		key=paramiko.RSAKey.from_private_key_file(self.pkey)
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(dest_hostname,username = 'rancho',pkey=key)
		
		transport = paramiko.Transport((dest_hostname, 22))
		transport.connect(username='rancho', pkey=key)
		sftp = paramiko.SFTPClient.from_transport(transport)
		stdin,stdout,stderr=ssh.exec_command('sudo test -f '+self.src_homeqtar_dir+' && sudo rm -rf '+self.src_homeqtar_dir)
		if not stdout.channel.recv_exit_status():
			print ' rm -rf oldefile '+self.src_homeqtar_dir
		
		sftp.put(self.local_homeqtar_dir,self.src_homeqtar_dir) 
		stdin,stdout,stderr=ssh.exec_command('sudo tar -xf '+self.src_homeqtar_dir+' -C /tmp/')
		if not stdout.channel.recv_exit_status():
			print 'sudo tar -xf '+self.src_homeqtar_dir+' -C /tmp/   '+ "done"
		
		stdin,stdout,stderr=ssh.exec_command('sudo test -f '+self.src_homeqtar_dir+' && sudo rm -rf '+self.src_homeqtar_dir)
		if not stdout.channel.recv_exit_status():
			print ' rm -rf  '+self.src_homeqtar_dir
		sftp.close()
		ssh.close()
		print 'homeq_put_untar {} done'.format(dest_hostname)
	def homeq_clean(self):
		key=paramiko.RSAKey.from_private_key_file(self.pkey)
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(self.src_hostname,username = 'rancho',pkey=key)
		stdin,stdout,stderr=ssh.exec_command('sudo test -f '+self.src_homeqtar_dir+' && sudo rm -rf '+self.src_homeqtar_dir)
		if not stdout.channel.recv_exit_status():
			print ' rm -rf oldefile '+self.src_homeqtar_dir
		
		if os.path.exists(self.local_homeqtar_dir):
			os.remove(self.local_homeqtar_dir)	
		print 'homeq_clean {} and local done'.format(self.src_hostname)


if  __name__ == '__main__':
	src_hostname='t2v.plat.bjtb.pdtv.it'
	dest_hostname='t3v.plat.bjtb.pdtv.it'
	
	datetime=time.strftime("%Y%m%d%H%M", time.localtime())
	#src_homeqtar_file='homeq_'+src_hostname+'_'+datetime+'.tar.gz'
	src_homeqtar_file='homeq_t2v.plat.bjtb.pdtv.it_201808221140.tar.gz'

	src_homeqtar_dir='/tmp/'+src_homeqtar_file
	local_homeqtar_dir='/home/liqingbin/ops_tools/homeq_copy/'+src_homeqtar_file
	pkey='/home/liqingbin/rancho/.ssh/id_rsa'
	
	paramiko.util.log_to_file('paramiko.log')
	
	q=Homeq_Copy(pkey,src_hostname,src_homeqtar_dir,local_homeqtar_dir)
	q.homeq_tar()
	q.homeq_tar_get()
	q.homeq_put_untar(dest_hostname)
	q.homeq_clean()
