### 部署方法

```
ansible -i add all -m copy -a "src=loginfo.pl dest=/home/liufeng/ owner=liufeng group=liufeng mode=755" -k -K -s

```
