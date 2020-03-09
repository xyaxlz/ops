package main

import (
	"bytes"
	"database/sql"
	"fmt"
	_ "github.com/go-sql-driver/mysql"
	"net"
	"os/exec"
	"regexp"
	"strings"
)

//定义连接127.0.0.1 数据库账号密码
var (
	userName  = "root"
	password  = "xxx"
	password2 = "xxxx"
	//ip = "xxx"
	ip     = "127.0.0.1"
	port   = "3388"
	dbName = "mysql"
)

//定义连接远程mysql元数据的账号和密码
var (
	regUserName = "dbreg"
	regPassword = "xxxx"
	//regIp = "127.0.0.1"
	regIp     = "xxx"
	regDbName = "db_asset"
	regPort   = "3388"
)

var DB *sql.DB

/*
连接127.0.0.1 数据库函数 如果第一个密码不对会使用第二密码重试，并把密码改成第一个密码。
创建monitor_dba和inception 账户，
如果dump进程数不为0，说明是主库，查询主库dump进程的客户端ip就是从库ip
如果主库dump进程数量或者从库io进程数量为0，说明数据库没有主从结构,如果不为0侧是主库或者从库

*/
func InitDB(port string) (ipArr []string, dbs []string, sum int, flag bool) {
	//定义存储从库ip数组
	var slavehosts []string
	//定义存储数据库名字数组
	var schemas []string
	//定义dump进程数和从库io进程数变量
	var count int
	//获取本机地址
	ipAddr := localIp()
	//定义数据库连接路径
	path := strings.Join([]string{userName, ":", password, "@tcp(", ip, ":", port, ")/", dbName, "?charset=utf8"}, "")
	//fmt.Println(path)
	//连接数据库
	DB, _ = sql.Open("mysql", path)

	//判断数据库是否连接成功，如果失败进入函数
	if err := DB.Ping(); err != nil {
		//定义数据库连接路径
		path = strings.Join([]string{userName, ":", password2, "@tcp(", ip, ":", port, ")/", dbName, "?charset=utf8"}, "")
		//连接数据库
		DB, _ = sql.Open("mysql", path)
		//fmt.Printf("open %s %s database fail\n", ip, port)
		fmt.Printf("open %s %s database fail\n", ipAddr, port)
		//更改数据库root密码
		_, err = DB.Query(" GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' IDENTIFIED BY PASSWORD 'xxxxx' WITH GRANT OPTION;")
		_, err = DB.Query(" GRANT ALL PRIVILEGES ON *.* TO 'root'@'127.0.0.1' IDENTIFIED BY PASSWORD 'xxxx' WITH GRANT OPTION;")
		//返回 变量，目前都为空，退出
		return slavehosts, schemas, count, false
	}
	//fmt.Printf("connect %s %s  sucess\n", ip, port)
	//创建monitor_dba 和inception账号
	_, _ = DB.Query("GRANT all ON *.* TO 'monitor_dba'@'xxxx' IDENTIFIED BY 'xxx';")
	_, _ = DB.Query("GRANT all ON *.* TO 'monitor_dba'@'xxx' IDENTIFIED BY 'xxxx';")
	_, _ = DB.Query("grant ALL  on *.* to inception@'xxx' IDENTIFIED BY 'xxxx'; ")
	_, _ = DB.Query("grant ALL  on *.* to inception@'xxx' IDENTIFIED BY 'xxx';")

	//查询dump进程，如果有数据说明是主库
	rows, _ := DB.Query("select HOST  from information_schema.processlist where COMMAND='Binlog Dump';")
	//定义延迟关闭
	defer rows.Close()
	//fmt.Println(err)
	//扫描查询出来的数据
	for rows.Next() {
		//定义存储从库ip 的变量
		var host string
		//扫描host 数据并赋予host变量
		err := rows.Scan(&host)
		checkErr(err)
		//如果host数据长度非0，也就是非空，去掉端口号，只取ip，并添加到slavehosts数组中
		if len(host) != 0 {
			//fmt.Println(port)
			host = strings.Split(host, ":")[0]
			slavehosts = append(slavehosts, host)
			//fmt.Println(host)

		}
	}

	//获取数据库名
	rows2, _ := DB.Query("select SCHEMA_NAME  from information_schema.SCHEMATA  where SCHEMA_NAME not in ('information_schema','mysql','performance_schema','test','mysql_identity')")
	defer rows2.Close()
	//fmt.Println(err)
	//把数据库名放入shcema数组
	for rows2.Next() {
		var schema string
		err := rows2.Scan(&schema)
		checkErr(err)
		if len(schema) != 0 {
			schemas = append(schemas, schema)
			//fmt.Println(schemas)

		}
	}

	//获取dump进程或者slave io进程数
	rows1, _ := DB.Query("select count(*)  from information_schema.processlist where COMMAND='Binlog Dump' or State like '%Slave has read all relay log%';")
	for rows1.Next() {
		err := rows1.Scan(&count)
		checkErr(err)

	}
	//fmt.Println(slavehosts,count)

	//返回从库ip数组 数据库名数组 和dump进程或者io进程数量
	return slavehosts, schemas, count, true
}

//把获取的从库ip数组，和数据库名数组，插入到远程元数据数据库
func regDB(slaveIpArr []string, dbs []string, masterIp string, sum int, masterPort string) {
	//把数据库名数组转化为空格分隔的字符串
	dbsName := strings.Join(dbs, " ")
	fmt.Println(dbsName)
	//生成数据库连接地址
	regPath := strings.Join([]string{regUserName, ":", regPassword, "@tcp(", regIp, ":", regPort, ")/", regDbName, "?charset=utf8"}, "")
	//fmt.Println(regPath)
	//连接数据库
	regDB, _ := sql.Open("mysql", regPath)
	//判断数据库是否连接成功，如果失败打印日志到中断，并退出
	if err := regDB.Ping(); err != nil {
		fmt.Printf("open %s %s database fail\n", regIp, regPort)
		return
	}
	//fmt.Printf("connect %s %s sucess\n",regIp, regPort)

	//prepare insert 语句
	stmt, err := regDB.Prepare(`insert into mysql_asset (ip,port,mip,flag,dbs) values (?, ?, ?, ?, ?)  ON DUPLICATE KEY UPDATE  mip=values(mip),flag=values(flag)`)
	checkErr(err)

	//如果dump进程或者slave io进程数为0，说明是单实例。远程注册为单实例数据库flag标识为2
	if sum == 0 {
		//_, err := stmt.Exec(masterIp, masterPort, "", "2", dbs)
		_, err := stmt.Exec(masterIp, masterPort, "", "2", dbsName)
		checkErr(err)
		//fmt.Printf("insert into mysql_asset (ip,port,mip,flag,dbs) values (%s, %s, %s, %s)  ON DUPLICATE KEY UPDATE  mip=values(mip),flag=values(flag)\n",masterIp, masterPort, "", "2", dbs)
		fmt.Printf("insert into mysql_asset (ip,port,mip,flag,dbs) values (%s, %s, %s, %s, %s)  ON DUPLICATE KEY UPDATE  mip=values(mip),flag=values(flag)\n", masterIp, masterPort, "", "2", dbsName)

	}

	//如果从库ip非空，说明本机是主库,flag 为1
	//远程注册本机+端口为主库ip
	if len(slaveIpArr) != 0 {
		//_, err := stmt.Exec(masterIp, masterPort, "", "1")
		_, err := stmt.Exec(masterIp, masterPort, "", "1", dbsName)
		checkErr(err)
		fmt.Printf("insert into mysql_asset (ip,port,mip,flag,dbs) values (%s, %s, %s, %s, %s)  ON DUPLICATE KEY UPDATE  mip=values(mip),flag=values(flag)\n", masterIp, masterPort, "", "1", dbsName)

	}

	//循环从库ip数组远程注册到元数据库 flag为0
	//远程注册从库ip和端口到元数据库
	for _, slaveIp := range slaveIpArr {
		//fmt.Printf("insert into msyqlasset (ip,port,mip,flag) valuses (%s, %s, %s, %s)\n",slaveIp,masterPort,masterIp,"0")
		//_, err1 := stmt.Exec(slaveIp, masterPort, masterIp, "0")
		_, err1 := stmt.Exec(slaveIp, masterPort, masterIp, "0", dbsName)
		checkErr(err1)
		fmt.Printf("insert into mysql_asset (ip,port,mip,flag,dbsName) values (%s, %s, %s, %s, %s)  ON DUPLICATE KEY UPDATE  mip=values(mip),flag=values(flag)\n", slaveIp, masterPort, masterIp, "0", dbsName)

	}

}

//校验ip是否正确函数，本程序没使用，为后期做准备
func checkIp(ip string) bool {
	addr := strings.Trim(ip, " ")
	regStr := `^(([1-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.)(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){2}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$`
	if match, _ := regexp.MatchString(regStr, addr); match {
		fmt.Println("true")
		return true
	}
	fmt.Println("false")
	return false
}

// 判断ip是否在16位网段中
func NetContainIP(netIP string, IP string) bool {
	//生产16位子网掩码。
	mask := net.IPv4Mask(byte(255), byte(255), byte(255), byte(0))
	//生成网段地址
	netMask := &net.IPNet{net.ParseIP(netIP), mask}
	//判断ip是否在网段中
	return netMask.Contains(net.ParseIP(IP))

}

//获取本机ip 排除回环地址 dock网卡 排除子网掩码是32位的vip
//func localIp() (reipAddr []string) {
func localIp() string {
	var ipAddr []string
	//获取所有的网卡。
	netInterfaces, err := net.Interfaces()
	if err != nil {
		fmt.Println("net.Interfaces failed, err", err.Error())
	}
	for i := 0; i < len(netInterfaces); i++ {
		// 排除没有启动的网卡，和以dock开头的网卡（docker启动的网卡）。
		if (netInterfaces[i].Flags&net.FlagUp) != 0 && !strings.Contains(netInterfaces[i].Name, "dock") {
			// 获取网卡地址。
			addrs, _ := netInterfaces[i].Addrs()
			for _, address := range addrs {
				// 排除本机回环地址 和子网掩码为32位的vip
				if ipnet, ok := address.(*net.IPNet); ok && !ipnet.IP.IsLoopback() && !strings.EqualFold(ipnet.Mask.String(), "ffffffff") {
					// 过滤不能转换位ipv4 和192.168.0.0/24 网段的地址。
					if ipnet.IP.To4() != nil && !NetContainIP("192.168.0.0", ipnet.IP.String()) {
						//if ipnet.IP.To4() != nil {
						//fmt.Println(ipnet.IP.String())
						ipAddr = append(ipAddr, ipnet.IP.String())
					}
				}
			}

		}
	}
	//fmt.Println(ipAddr)
	//fmt.Println(strings.Join(ipAddr, ","))
	return strings.Join(ipAddr, ",")
}

//go 调用shell命令函数，返回shell命令返回值
func execShell(s string) (string, error) {
	cmd := exec.Command("/bin/bash", "-c", s)
	var out bytes.Buffer
	cmd.Stdout = &out
	err := cmd.Run()
	checkErr(err)
	return out.String(), err

}

//校验err是否为空如果为空输出错误panic退出
func checkErr(err error) {

	if err != nil {
		fmt.Println(err)
		panic(err)

	}

}

//主函数
func main() {
	//获取本机ip地址
	ipAddr := localIp()
	//fmt.Println(ipAddr)
	//获取mysqld进程监听端口
	mysqlPorts, err := execShell("netstat  -lntp |grep mysqld|awk '{print $4}'|awk -F ':' '{print $NF}' |sort|uniq")
	checkErr(err)
	//fmt.Println(mysqlPorts)
	//将mysqld端口转换为数组
	mysqlPortsArr := strings.Fields(mysqlPorts)
	fmt.Println(mysqlPortsArr, len(mysqlPortsArr))
	//循环mysqld端口
	for _, port := range mysqlPortsArr {
		//获取数据库从库ip，数据库名字，dump进程或者slaveio进程数
		if slaveIps, dbs, sum, ok := InitDB(port); ok {
			//注册数据库信息到远程元数据库
			regDB(slaveIps, dbs, ipAddr, sum, port)
		}
		fmt.Println(port)
	}
	//checkIp("10.11.22.s24")
	//ok := NetContainIP("192.168.2.0", "192.168.2.5")
	//fmt.Println(ok)

}
