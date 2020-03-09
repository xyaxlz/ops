ansible -i add all -m copy -a "src=pkgs_del.sh dest=/home/server_config/monitor/bin/ mode=755 " -k -K -s
