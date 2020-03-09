#!/bin/bash
#a=($(find /home/q  -type l -exec ls -l {} \;  |awk -F '->'  '{print $2}'|grep '/home/q/pkgs/'  |awk -F '-' '{print $1}' |sort  -n |uniq ))
#b=($(ls  /home/q/pkgs/*  -d|awk -F '-' '{print $1 }' |sort  -n |uniq ))
#echo ${#a[@]}
#echo ${#b[@]}

#for i in ${b[@]}
#do
#	#echo $i
#	if ! [[ "${a[@]}" =~ $i ]];then
#		echo $i
#	fi
#done


rm -f  /home/q/pkgs/*.gz
#tar -cvf /data/pkgs_`date +%Y%m%d%H%M`.tar /home/q/pkgs
arrlinks=($(find /home/q  -type l -exec ls -l {} \;  |awk -F '->'  '{print $2}'|grep '/home/q/pkgs/'))
arrpkgs=($(ls  /home/q/pkgs/*  -d ))

for i in ${arrpkgs[@]}
do
	#echo $i
	#if ! [[ "${arrlinks[@]}" =~ $i ]];then
	if ! echo  "${arrlinks[@]}" |grep -w $i >/dev/null;then

		if  echo $i |grep '/home/q/pkgs/' >/dev/null;then
			echo $i
			rm -rf $i
		fi
	fi
done
