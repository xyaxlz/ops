package main

import (
	"database/sql"
	"encoding/base64"
	"fmt"
	_ "github.com/go-sql-driver/mysql"
	"net/smtp"
	"strings"
	"time"
)

func checkErr(err error) {
	if err != nil {
		fmt.Println(err)
		panic(err)
	}
}

var (
	userName = "dbms"
	password = "xxxx"
	dbIp     = "xxx"
	port     = "3306"
	dbName   = "dbms"
)

var DB *sql.DB

func dbQueryCount(DB *sql.DB, sql string) (count string) {

	rows := DB.QueryRow(sql)
	err := rows.Scan(&count)
	checkErr(err)
	return count

}
func dbQueryDesc(DB *sql.DB, sql string) (rowsDesc string) {
	var bakIp string
	var bakPort string
	//var rowsDesc string
	var rowsArr []string

	rows, _ := DB.Query(sql)
	defer rows.Close()
	for rows.Next() {
		err := rows.Scan(&bakIp, &bakPort)
		checkErr(err)
		rowsArr = append(rowsArr, bakIp+":"+bakPort)
	}
	rowsDesc = strings.Join(rowsArr, " ")
	fmt.Println(rowsDesc)
	return rowsDesc

}

func getDBbackStatus() (checkTime string, backTime string, sucessCount string, failCount string, failDesc string, runningCount string, runDesc string, otherCount string, otherDesc string) {

	path := strings.Join([]string{userName, ":", password, "@tcp(", dbIp, ":", port, ")/", dbName, "?charset=utf8"}, "")
	DB, _ = sql.Open("mysql", path)
	if err := DB.Ping(); err != nil {
		fmt.Printf("open %s %s database fail\n", dbIp, port)
	}
	checkTime = time.Now().Format("2006-01-02 15:04:05")
	//checkTime = fmt.Sprintf("%d-%d-%d %d:%d:%d", t1.Year(), t1.Month(), t1.Day(), t1.Hour(), t1.Minute(), t1.Second())

	t2 := time.Now().AddDate(0, 0, -3)
	//old1Time := fmt.Sprintf("%d%d%d", t2.Year(), t2.Month(), t2.Day())
	//backTime = fmt.Sprintf("%d-%d-%d", t2.Year(), t2.Month(), t2.Day())
	old1Time := t2.Format("20060102")
	backTime = t2.Format("2006-01-02")
	fmt.Println(time.Now().AddDate(0, 0, -1).Format(time.RFC3339))
	fmt.Println("oldTime:" + old1Time + " backTime:" + backTime)
	sql1 := "select count(*) from  backup_info where db_type='mysql' and bak_type in ('xtrabackup','mysqldump') and file_dir like '%" + old1Time + "%' and message='compress success';"
	sucessCount = dbQueryCount(DB, sql1)
	fmt.Println(sql1)

	sql2 := "select count(*) from  backup_info where db_type='mysql' and bak_type in ('xtrabackup','mysqldump') and start_time >='" + backTime + "' and status=2;"
	failCount = dbQueryCount(DB, sql2)
	fmt.Println(sql2)
	if failCount != "0" {
		sql21 := "select ip, port from  backup_info where db_type='mysql' and bak_type in ('xtrabackup','mysqldump') and start_time >='" + backTime + "' and status=2;"
		//sql21 := "select ip,port  from  backup_info where db_type='mysql' and bak_type in ('xtrabackup','mysqldump') and start_time <='2019-10-31' and status=2;"
		failDesc = dbQueryDesc(DB, sql21)
		fmt.Println(sql21)

	}

	sql3 := "select count(*) from  backup_info where db_type='mysql' and bak_type in ('xtrabackup','mysqldump') and file_dir like '%" + old1Time + "%' and (message like '%run%' or message = 'success');"
	runningCount = dbQueryCount(DB, sql3)
	fmt.Println(sql3)
	if runningCount != "0" {
		sql31 := "select ip, port from  backup_info where db_type='mysql' and bak_type in ('xtrabackup','mysqldump') and file_dir like '%" + old1Time + "%' and (message like '%run%' or message = 'success');"
		runDesc = dbQueryDesc(DB, sql31)
		fmt.Println(sql31)

	}

	sql4 := "select count(*) from  backup_info where db_type='mysql' and bak_type in ('xtrabackup','mysqldump') and file_dir like '%" + old1Time + "%' and (message not like '%fail%'" +
		" and message not like '%run%' and message not like '%success%');"
	otherCount = dbQueryCount(DB, sql4)
	fmt.Println(sql4)
	if otherCount != "0" {
		sql41 := "select ip, port  from  backup_info where db_type='mysql' and bak_type in ('xtrabackup','mysqldump') and file_dir like '%" + old1Time + "%' and (message not like '%fail%'" +
			" and message not like '%run%' and message not like '%success%');"
		otherDesc = dbQueryDesc(DB, sql41)
		fmt.Println(sql41)

	}

	return checkTime, backTime, sucessCount, failCount, failDesc, runningCount, runDesc, otherCount, otherDesc

}

func getMDBbackStatus() (mdbCheckTime string, mdbBackTime string, mdbSucessCount string, mdbFailCount string, mdbFailDesc string, mdbRunningCount string, mdbRunDesc string, mdbOtherCount string, mdbOtherDesc string) {

	path := strings.Join([]string{userName, ":", password, "@tcp(", dbIp, ":", port, ")/", dbName, "?charset=utf8"}, "")
	DB, _ = sql.Open("mysql", path)
	if err := DB.Ping(); err != nil {
		fmt.Printf("open %s %s database fail\n", dbIp, port)
	}
	mdbCheckTime = time.Now().Format("2006-01-02 15:04:05")
	//checkTime = fmt.Sprintf("%d-%d-%d %d:%d:%d", t1.Year(), t1.Month(), t1.Day(), t1.Hour(), t1.Minute(), t1.Second())

	t2 := time.Now().AddDate(0, 0, -3)
	//old1Time := fmt.Sprintf("%d%d%d", t2.Year(), t2.Month(), t2.Day())
	//backTime = fmt.Sprintf("%d-%d-%d", t2.Year(), t2.Month(), t2.Day())
	old1Time := t2.Format("20060102")
	mdbBackTime = t2.Format("2006-01-02")
	fmt.Println(time.Now().AddDate(0, 0, -1).Format(time.RFC3339))
	fmt.Println("oldTime:" + old1Time + " backTime:" + mdbBackTime)
	sql1 := "select count(*) from  backup_info where db_type='mongodb' and bak_type in ('mongodump') and file_dir like '%" + old1Time + "%' and message='compress success';"
	mdbSucessCount = dbQueryCount(DB, sql1)
	fmt.Println(sql1)

	sql2 := "select count(*) from  backup_info where db_type='mongodb' and bak_type in ('mongodump') and start_time >='" + mdbBackTime + "' and status=2;"
	mdbFailCount = dbQueryCount(DB, sql2)
	fmt.Println(sql2)
	if mdbFailCount != "0" {
		sql21 := "select ip, port from  backup_info where db_type='mongodb' and bak_type in ('mongodump') and start_time >='" + mdbBackTime + "' and status=2;"
		//sql21 := "select ip,port  from  backup_info where db_type='mysql' and bak_type in ('xtrabackup','mysqldump') and start_time <='2019-10-31' and status=2;"
		mdbFailDesc = dbQueryDesc(DB, sql21)
		fmt.Println(sql21)

	}

	sql3 := "select count(*) from  backup_info where db_type='mongodb' and bak_type in ('mongodump') and file_dir like '%" + old1Time + "%' and (message like '%run%' or message = 'success');"
	mdbRunningCount = dbQueryCount(DB, sql3)
	fmt.Println(sql3)
	if mdbRunningCount != "0" {
		sql31 := "select ip, port from  backup_info where db_type='mongodb' and bak_type in ('mongodump') and file_dir like '%" + old1Time + "%' and (message like '%run%' or message = 'success');"
		mdbRunDesc = dbQueryDesc(DB, sql31)
		fmt.Println(sql31)

	}

	sql4 := "select count(*) from  backup_info where db_type='mongodb' and bak_type in ('mongodump') and file_dir like '%" + old1Time + "%' and (message not like '%fail%'" +
		" and message not like '%run%' and message not like '%success%');"
	mdbOtherCount = dbQueryCount(DB, sql4)
	fmt.Println(sql4)
	if mdbOtherCount != "0" {
		sql41 := "select ip, port  from  backup_info where db_type='mongodb' and bak_type in ('mongodump') and file_dir like '%" + old1Time + "%' and (message not like '%fail%'" +
			" and message not like '%run%' and message not like '%success%');"
		mdbOtherDesc = dbQueryDesc(DB, sql41)
		fmt.Println(sql41)

	}

	return mdbCheckTime, mdbBackTime, mdbSucessCount, mdbFailCount, mdbFailDesc, mdbRunningCount, mdbRunDesc, mdbOtherCount, mdbOtherDesc

}

//func getRedisBackStatus() (RedisCheckTime string, RedisBackTime string, YZRedisSucessCount string, YZRedisFailCount string, YZRedisFailDesc string) {
func getRedisBackStatus() (RedisBackTime string, YZRedisSucessCount string, YZRedisFailCount string, YZRedisFailDesc string) {

	path := strings.Join([]string{userName, ":", password, "@tcp(", dbIp, ":", port, ")/", dbName, "?charset=utf8"}, "")
	DB, _ = sql.Open("mysql", path)
	if err := DB.Ping(); err != nil {
		fmt.Printf("open %s %s database fail\n", dbIp, port)
	}
	//RedisCheckTime := time.Now().Format("2006-01-02 15:04:05")
	//checkTime = fmt.Sprintf("%d-%d-%d %d:%d:%d", t1.Year(), t1.Month(), t1.Day(), t1.Hour(), t1.Minute(), t1.Second())

	t2 := time.Now().AddDate(0, 0, 0)
	//old1Time := fmt.Sprintf("%d%d%d", t2.Year(), t2.Month(), t2.Day())
	//backTime = fmt.Sprintf("%d-%d-%d", t2.Year(), t2.Month(), t2.Day())
	old1Time := t2.Format("20060102")
	RedisBackTime = t2.Format("2006-01-02")
	fmt.Println(time.Now().AddDate(0, 0, -1).Format(time.RFC3339))
	fmt.Println("oldTime:" + old1Time + " RedisBackTime" + RedisBackTime)
	sql1 := "select count(*)  from codis_back where flag='sucess' and bakip like '%10.100.86%' and backtime >='" + RedisBackTime + "'"
	YZRedisSucessCount = dbQueryCount(DB, sql1)
	fmt.Println(sql1)

	sql2 := "select count(*)  from codis_back where flag='fail' and bakip like '%10.100.86%' and backtime >='" + RedisBackTime + "'"
	//sql2 := "select count(*)  from codis_back where flag='fail' and bakip like '%10.100.86%'"
	YZRedisFailCount = dbQueryCount(DB, sql2)
	if YZRedisFailCount != "0" {
		sql21 := "select bakip,bakport  from codis_back where flag='fail' and bakip like '%10.100.86%' and backtime >='" + RedisBackTime + "'"
		//sql21 := "select bakip,bakport  from codis_back where flag='fail' and bakip like '%10.100.86%'"
		YZRedisFailDesc = dbQueryDesc(DB, sql21)
		fmt.Println(sql21)
	}

	return RedisBackTime, YZRedisSucessCount, YZRedisFailCount, YZRedisFailDesc
}

func sendMail(addr string, from string, subject string, body string, to string) error {
	r := strings.NewReplacer("\r\n", "", "\r", "", "\n", "", "%0a", "", "%0d", "")
	c, err := smtp.Dial(addr)
	checkErr(err)
	defer c.Close()
	err = c.Mail(r.Replace(from))
	checkErr(err)

	for _, i := range strings.Split(r.Replace(to), ";") {
		err = c.Rcpt(r.Replace(i))
		checkErr(err)
	}

	w, err := c.Data()
	checkErr(err)

	msg := "To: " + to + "\r\n" +
		"From: " + from + "\r\n" +
		"Subject: " + subject + "\r\n" +
		"Content-Type: text/html; charset=\"UTF-8\"\r\n" +
		"Content-Transfer-Encoding: base64\r\n" +
		"\r\n" + base64.StdEncoding.EncodeToString([]byte(body))

	_, err = w.Write([]byte(msg))
	checkErr(err)

	err = w.Close()
	checkErr(err)

	return c.Quit()

}

func main() {
	mdbCheckTime, mdbBackTime, mdbSucessCount, mdbFailCount, mdbFailDesc, mdbRunningCount, mdbRunDesc, mdbOtherCount, mdbOtherDesc := getMDBbackStatus()
	fmt.Println("mdbCheckTime: " + mdbCheckTime)
	fmt.Println("mdbBackTime: " + mdbBackTime)
	fmt.Println("mdbSucessCount: " + mdbSucessCount)
	fmt.Println("mdbFailCount: " + mdbFailCount)
	fmt.Println("mdbFailDesc: " + mdbFailDesc)
	fmt.Println("mdbRunningCount: " + mdbRunningCount)
	fmt.Println("mdbRunDesc: " + mdbRunDesc)
	fmt.Println("mdbOtherCount: " + mdbOtherCount)
	fmt.Println("mdbOtherDesc: " + mdbOtherDesc)

	checkTime, backTime, sucessCount, failCount, failDesc, runningCount, runDesc, otherCount, otherDesc := getDBbackStatus()
	RedisBackTime, YZRedisSucessCount, YZRedisFailCount, YZRedisFailDesc := getRedisBackStatus()

	body := `
					                <html>
					                <body>
					                <table border="1" cellspacing="0" width="1700"  style="border-collapse:collapse;">
							<tr>
					                        <td><font size="3" >备份检查时间 </font></td>
								<td colspan=6 align='left' ><font size="3" >` + checkTime + `</font></td>
							</tr>
					                <tr>
					                        <td width="160"><font size="3" >备份类型 </font></td>
					                        <td width="250"><font size="3">` + "MySQL" + `</font></td>
					                        <td width="100"><font size="3">详细</font></td>
					                        <td width="250"><font size="3">` + "MongoDB" + `</font></td>
					                        <td width="100"><font size="3">详细</font></td>
					                        <td width="250"><font size="3">` + "Codis_YZ" + `</font></td>
					                        <td width="100"><font size="3">详细</font></td>
					                </tr>
					                <tr>
					                        <td><font size="3" >备份时间 </font></td>
					                        <td><font size="3">` + backTime + `</font></td>
					                        <td></td>
					                        <td><font size="3">` + mdbBackTime + `</font></td>
					                        <td></td>
					                        <td><font size="3">` + RedisBackTime + `</font></td>
					                        <td></td>
					                </tr>
					                <tr>
					                        <td><font size="3" >备份成功数量 </font></td>
					                        <td><font size="3">` + sucessCount + `</font></td>
					                        <td></td>
					                        <td><font size="3">` + mdbSucessCount + `</font></td>
					                        <td></td>
					                        <td><font size="3">` + YZRedisSucessCount + `</font></td>
					                        <td></td>
					                </tr>
					                <tr>
					                        <td><font size="3">备份失败数量</font></td>
					                        <td><font size="3" color="red">` + failCount + `</font></td>
					                        <td><font size="3">` + failDesc + `</font></td>
					                        <td><font size="3" color="red">` + mdbFailCount + `</font></td>
					                        <td><font size="3">` + mdbFailDesc + `</font></td>
					                        <td><font size="3" color="red">` + YZRedisFailCount + `</font></td>
					                        <td><font size="3">` + YZRedisFailDesc + `</font></td>
					                </tr>
					                <tr>
					                        <td><font size="3">备份中数量</font></td>
					                        <td><font size="3" color="blue">` + runningCount + `</font></td>
					                        <td><font size="3">` + runDesc + `</font></td>
					                        <td><font size="3" color="blue">` + mdbRunningCount + `</font></td>
					                        <td><font size="3">` + mdbRunDesc + `</font></td>
					                        <td></td>
					                        <td></td>
					                </tr>
					                <tr>
					                        <td><font size="3">其它异常数量</font></td>
					                        <td><font size="3" color="red">` + otherCount + `</font></td>
					                        <td><font size="3">` + otherDesc + `</font></td>
					                        <td><font size="3" color="red">` + mdbOtherCount + `</font></td>
					                        <td><font size="3">` + mdbOtherDesc + `</font></td>
					                        <td></td>
					                </tr>
					                </table>


					                </body>
					                </html>
					                `

	mailHead := "数据库备份检查_" + backTime
	//sendMail("192.168.7.77:25", "dbamonitor@zhangyue.com", mailHead, body, "dba.list@zhangyue.com;yangming@zhangyue.com")
	sendMail("192.168.7.77:25", "dbamonitor@zhangyue.com", mailHead, body, "liqingbin@zhangyue.com")

}
