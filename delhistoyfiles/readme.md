
# 删除指定目录下，最后修改时间早于指定时间的文件，时间粒度：小时
# 配置文件格式 ：  需清理的目录=小时数
# 需要清理的路径用真实路径，不要用软连接

# 部署方法
# ansible-playbook  -i txhosts  -e "hosts=ip1v.infra.sht.pdtv.it" delhistory.yaml  -k -K -s
