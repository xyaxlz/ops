#!/bin/bash
#yum -y install smartmontools
export PATH="${PATH}:/usr/local/bin:/usr/bin:/bin:/usr/libexec"
export PATH="${PATH}:/usr/local/sbin:/usr/sbin:/sbin"
export PATH="${PATH}:/opt/MegaRAID/MegaCli/"
PID=$$
restr="{\"data\":[ "
if MegaCli64 -PDList -aALL >/tmp/isl 2>/dev/null; then
for dev in $(awk '/Device Id/{print $3}' /tmp/isl); do
idev="$(sed -e '/./{H;$!d;}' -e "x;/Device Id: ${dev}/!d;" /tmp/isl|awk '/Device Id/{d=$3}/Inquiry Data/{if ($0 ~ /INTEL/) {printf("%d\n", d)}}')"
              if [ -n "${idev}" ]; then
                  restr=$restr"{ ${idev}},"
              fi
        done
        if ! ps -p ${PID} >/dev/null 2>&1; then
              break;
        fi
    fi
    length=${#restr}
    l=$[length-1]
    substr=${restr:0:l}
#    echo $substr"]}"
    substr=$substr"]}"
    substr=${substr//\"/}
    substr=${substr//{/}
    substr=${substr//\}/}
    substr=${substr//data/}
    substr=${substr//[/}
    substr=${substr//]/}
    substr=${substr//:/}
#    echo "substr = "$substr
echo $substr >/tmp/ssdserviceID
i=`cat /tmp/ssdserviceID |sed 's/\( \)\+/\n/g'  |cut -d "," -f1`
for loop in $i
do
smartctl -a -d megaraid,$loop /dev/sdb |grep "Media_Wearout_Indicator" | awk -F ' ' '{print $4}'
smartctl -a -d megaraid,$loop /dev/mapper/VolGroup-lv_data ext4 |grep "Media_Wearout_Indicator" | awk -F ' ' '{print $4}'
done
