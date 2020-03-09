### 部署方法

```
ansible-playbook  -i add -e "hosts=all" ngxtop.yaml  -K -k -s
```
###需要修改ngxtop发送报警的主机名

####日志主机组##########
###########
s2,s5
###########
s4,log5v
###########
log5v,log6v
###########
s4,log6v
###########
s6,log7v
###########
log3v,log4v
###########
