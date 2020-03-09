for i in `ls /etc/redis/*`
do 
	a=`basename $i|awk -F '.' '{print $1}' `
	printf "$a "
	/usr/bin/redislogin_${a}  info|grep "used_memory_peak:"  
done
