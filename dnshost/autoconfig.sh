for i in `seq 5`
do
    IP=`ping badge${i}v.main.bjac.pdtv.it -c 1 |egrep -o "[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}"  |uniq`
    echo "'$IP  badge.pdtv.io'"
done
