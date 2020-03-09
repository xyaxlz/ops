export PATH=.:/sbin:/usr/sbin:/usr/local/sbin:/usr/local/bin:/bin:/usr/bin:/usr/local/bin
SCI_PATH=`dirname $0`
CUR_PATH=$SCI_PATH/
USER=${USER/-/_}
RG=/home/q/tools/pylon_rigger/rigger
#$RG  conf -e dev -s all
echo "build opstools src(is sdk modules)"
#$RG  restart
