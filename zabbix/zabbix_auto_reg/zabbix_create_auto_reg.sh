#!/bin/bash
cat  $1  |egrep -v "#|\[|^$"|sed 's/[0-9]\+//' |sort -n|uniq  >/tmp/$$.txt
while read line
do
    flag=`echo $line|awk -F '.' '{print $3}'`
    if ! [ $flag == "bjac" -o  $flag == "bjab"  -o $flag == "bjza" -o $flag == "soho" -o $flag == "sht" -o  $flag == "vnet" -o $flag == "bjtb" ] ;then
        continue
    fi
    #echo $flag
    #echo $line
    md5=`echo $line|md5sum|awk '{print $1}'`
    group=`echo $line|awk -F'.' '{printf "%s_%s_%s", $3,$2,$1}'`
    if [ ${group: -1} == "v" ] ;then
        group=${group%?}
    fi
    GROUP=$(echo $group | tr '[a-z]' '[A-Z]')
    if echo  $GROUP|egrep  "BJAC_|BJAZ_|SOHO_|VNET_" >/dev/null;then
	    if echo  $GROUP|grep  "INFRA_DB" >/dev/null;then
	        python bjac_create_auto_reg.py  -A ${GROUP}"_Auto_Registration" -H $group -M $md5 -G $GROUP -T "Template OS Linux MySQL"
	    elif echo  $GROUP|grep  "INFRA_RDB" >/dev/null ;then
	        python bjac_create_auto_reg.py  -A ${GROUP}"_Auto_Registration" -H $group -M $md5 -G $GROUP -T "Template OS  Linux Redis"
	    elif echo  $GROUP|grep  "INFRA_RCDB" >/dev/null;then
	        python bjac_create_auto_reg.py  -A ${GROUP}"_Auto_Registration" -H $group -M $md5 -G $GROUP -T "Template OS  Linux Redis"
	
	    elif echo  $GROUP|grep  "INFRA_SSDB" >/dev/null;then
	        python bjac_create_auto_reg.py  -A ${GROUP}"_Auto_Registration" -H $group -M $md5 -G $GROUP -T "Template OS  Linux SSDB"
	    elif echo  $GROUP|grep  "INFRA_MDB" >/dev/null;then
	        python bjac_create_auto_reg.py  -A ${GROUP}"_Auto_Registration" -H $group -M $md5 -G $GROUP -T "Template OS Linux MDB"
	    elif echo  $GROUP|grep  "BJZA" >/dev/null;then
	        python bjac_create_auto_reg.py  -A ${GROUP}"_Auto_Registration" -H $group -M $md5 -G $GROUP -T "Template OS Linux ops bjza"
	    else
	        python bjac_create_auto_reg.py  -A ${GROUP}"_Auto_Registration" -H $group -M $md5 -G $GROUP -T "Template OS Linux ops"
	    fi
    fi
    if echo  $GROUP|egrep  "BJTB_|VNET_" >/dev/null;then
	    if echo  $GROUP|grep  "INFRA_DB" >/dev/null;then
	        python sht_create_auto_reg.py  -A ${GROUP}"_Auto_Registration" -H $group -M $md5 -G $GROUP -T "Template OS Linux MySQL"
	    elif echo  $GROUP|grep  "INFRA_RDB" >/dev/null ;then
	        python sht_create_auto_reg.py  -A ${GROUP}"_Auto_Registration" -H $group -M $md5 -G $GROUP -T "Template OS  Linux Redis"
	    elif echo  $GROUP|grep  "INFRA_RCDB" >/dev/null;then
	        python sht_create_auto_reg.py  -A ${GROUP}"_Auto_Registration" -H $group -M $md5 -G $GROUP -T "Template OS  Linux Redis"
	
	    elif echo  $GROUP|grep  "INFRA_SSDB" >/dev/null;then
	        python sht_create_auto_reg.py  -A ${GROUP}"_Auto_Registration" -H $group -M $md5 -G $GROUP -T "Template OS  Linux SSDB"
	    elif echo  $GROUP|grep  "INFRA_MDB" >/dev/null;then
	        python sht_create_auto_reg.py  -A ${GROUP}"_Auto_Registration" -H $group -M $md5 -G $GROUP -T "Template OS Linux MDB"
	    elif echo  $GROUP|grep  "BJZA" >/dev/null;then
	        python sht_create_auto_reg.py  -A ${GROUP}"_Auto_Registration" -H $group -M $md5 -G $GROUP -T "Template OS Linux ops bjza"
	    else
	        python sht_create_auto_reg.py  -A ${GROUP}"_Auto_Registration" -H $group -M $md5 -G $GROUP -T "Template OS Linux ops"
	    fi
    fi
done < /tmp/$$.txt
