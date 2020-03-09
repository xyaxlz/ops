#!/bin/bash

# source data file
DEST_DATA=/tmp/iostat-data
TMP_DATA=/tmp/iostat-data.tmp

#
# gather data in temp file first, then move to final location
# it avoids zabbix-agent to gather data from a half written source file
#
# iostat -kx 10 2 - will display 2 lines :
#  - 1st: statistics since boot -- useless
#  - 2nd: statistics over the last 10 sec
#
iostat -kx 10 2 > $TMP_DATA
mv $TMP_DATA $DEST_DATA


