#! /usr/bin/python2.7

#Created zolker

'''
The main goal is do some MySQL operations batchly,

WARNING! When you use it to do DML/DDL operations,
strongly suggest that run the command with
--dry-run to see what will happen!!!

version 1.0: 2013-03-30
  *origin source from myisam2innodb.py.
version 1.1: 2013-06-09
  *--no-binlog option to record binlog for alter statement.
version 1.2: 2013-07-04
  *can multi threads for DML/DDL statement(fake multhreads)
version 1.3: 2013-07-15
  *when you do 'alter table engine=xxxx', if engine does't change,then we will
   do nothing
version 1.4: 2013-07-30
  *achieve real multi threads
version 1.5: 2013-08-28
  *refactor the code, support show/set/select command 
version 1.7: 2013-12-13
  *add show_hi option, rewrite the options parse code
'''

import argparse
import sys
import os
import stat
import socket
import time
import threading
import re
import logging
import copy
import MySQLdb
import subprocess 
from warnings import filterwarnings
import traceback
sys.path.append('/etc/db_tools')
from mysqllib import *
from syslib import *
filterwarnings('ignore', category = MySQLdb.Warning)

#global variables
db_black_list = ["mysql","performance_schema","zjmdmm","information_schema",\
                 "nagiosdmm","xddmm","tcdmm",]
mysql_user='db_admin'
mysql_passwd=''
VERSION='1.0'

##################################
LOG_PREFIX = "/tmp/"
logger_s = None #log for program internal
logger_u = None #log for user
##################################

def run_command(command):
    p = subprocess.Popen(command, shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
    return p.communicate()


def getLogger(user_log, log_level):
    system_log = "/tmp/mysql-login_YnzAtZxuldXq.log"
    if user_log and user_log.startswith("/"):
        log_dest = user_log
    elif user_log:
        log_dest = LOG_PREFIX + user_log
    else:
        log_dest = None
    logger_s = logging.getLogger("intertal-"+str(VERSION))
    logger_s.setLevel(logging.DEBUG)

    logger_u = logging.getLogger("user-"+str(VERSION))
    logger_u.setLevel(log_level)

    #if path is a dir, exit the program
    if log_dest and os.path.isdir(log_dest):
        print "system log destination(%s) is a dir, not a file!" % log_dest
        sys.exit(-1)
    if log_dest and os.path.isdir(system_log):
        print "user log destination(%s) is a dir, not a file!" % system_log 
        sys.exit(-1)
    #if file not exists, touch it  and it's permisson to 777
    if log_dest and not os.path.exists(log_dest):
        os.mknod(log_dest)
        os.chmod(log_dest, stat.S_IRWXU+stat.S_IRWXG+stat.S_IRWXO)
    if log_dest and not os.path.exists(system_log):
        os.mknod(system_log)
        os.chmod(system_log, stat.S_IRWXU+stat.S_IRWXG+stat.S_IRWXO)
    if not log_dest:
        file_handler_u = logging.StreamHandler(sys.stdout)
    else:
        file_handler_u = logging.FileHandler(log_dest)
    print "System log redirect to %s" % system_log
    print "User log redirect to %s" % (log_dest if log_dest else "STDOUT")
    print ""
    file_handler_s = logging.FileHandler(system_log)
    
    formatter_s = logging.Formatter("%(asctime)s - [%(levelname)s] - "+
           "[%(name)s/%(filename)s: %(lineno)d] - %(message)s")
    formatter_u = logging.Formatter("%(message)s")
    file_handler_s.setFormatter(formatter_s)
    file_handler_u.setFormatter(formatter_u)
    logger_s.addHandler(file_handler_s)
    logger_u.addHandler(file_handler_u)
    return logger_s, logger_u


class Connection:

    def __init__(self, *args, **kargs):
        self.args = args
        self.kargs = kargs
        self.kargs['user'] = kargs['user'] if kargs.has_key('user') \
                                           else opts.user
        self.kargs['passwd'] = kargs['passwd'] if kargs.has_key('passwd') \
                                               else opts.passwd
        self.kargs['connect_timeout'] = kargs['connect_timeout'] \
                                        if kargs.has_key('connect_timeout') \
                                        else 5
        # TODO: we need to overwrite other argument. 
        #      such interactive_timeout/wait_tiemout/charset and so on

    def get_connection(self,):
        ret = {'errno':0, 'errmsg':"", 'value':None}
        conn = None

        try:
            # TODO: add a connect retry mechaniam
	    #print self.kargs
            conn = MySQLdb.connect(*self.args, **self.kargs)
            ret['value'] = conn
        except Exception, err:
            ret['errno'] = 1
            ret['errmsg'] = str(err)
        finally:
            return ret

# Wrapper for MySQL connection
def get_connection(*args, **kargs):
    #must *args, **kargs, not args, kargs
    __conn__ = Connection(*args, **kargs)
    return __conn__.get_connection()

def close_connection(conn):
    ret = {'errno':0, 'msg':"close connection success", 'value':None}
    try:
        if conn:
            conn.close()
    except Exception, err:
        ret['errno'] = 1
        ret['msg'] = str(err)
    finally:
        return ret

def close_cursor(cursor):
    ret = {'errno':0, 'msg':"close cursor succuss", 'value':None}
    try:
        if cursor:
            cursor.close()
    except Exception, err:
        ret['errno'] = 1
        ret['msg'] = str(err)
    finally:
        return ret


connect = Connect = get_connection




class Common:

    T_SELECT = 1
    T_SHOW = 2
    T_TRUNCATE = 3
    T_DELETE = 4
    T_SET = 5
    T_ALTER = 6

    def __init__(self, sql_prefix, sql_suffix, db_list, tb_list):
        self.sql_prefix = sql_prefix
        self.sql_suffix = sql_suffix
        self.db_list = db_list
        self.tb_list = tb_list

    # FIXME: very ugly code. shouldn't occur here
    def get_engine(self, db, table):
        retv = {'errno':0, 'msg':'', 'value':'null'}
        conn = None
        cursor = None
        try:
            ret = connect(host=opts.host, db=db, port=opts.port)
            if ret['errno']:
                retv['errno'] = 1
                retv['errmsg'] = "connect(%s:%s) failed" % (opts.port, opts.port)
                return retv
            conn = ret['value']
            cursor = conn.cursor()
            cursor.execute("select engine from information_schema.tables where\
                           table_schema='%s' and table_name='%s'" % (db, table))
            res = cursor.fetchall()
            if len(res) > 0:
                retv['value'] = res[0][0]
            else:
                retv['errno'] = 2
                retv['msg'] = "table %s not exists or isn't a base table" % table
        except Exception, err:
            retv['errno'] = -1
            retv['msg'] = str(err)
            logger_s.error(str(err))
            logger_u.error("Failed: %s" % str(err))
        finally:
            close_cursor(cursor)
            close_connection(conn)



class MySQLQuery:

    def __init__(self, common):
        self.common = common

    # Get table list from a db
    def get_tables_by_db(self, db):
        retv = {'errno':0, 'msg':'', 'value':[]}
        c = self.common
        if len(c.tb_list) > 0:
            retv['value'] = c.tb_list
            return retv
        tbs = []
        conn = cursor = None
        try:
            ret = connect(host=opts.host, db=db, port=opts.port)
            if ret['errno']:
                retv['errno'] = 1
                retv['msg'] = "connect(%s:%s) failed:%s" % \
                               (opts.host, opts.port, ret['errmsg'])
                return retv 
            conn = ret['value']
            cursor = conn.cursor()
            cursor.execute("show tables")
            tmp_tb = cursor.fetchall()
            for tb in tmp_tb:
                if opts.tb_prefix and not tb[0].startswith(opts.tb_prefix):
                    continue
                tbs.append(tb[0])
            retv['value'] = tbs
        except Exception, err:
            retv['errno'] = -1
            retv['msg'] = str(err)
            logger_s.error(str(err))
            logger_u.error("Failed: %s" % str(err))
        finally:
            close_cursor(cursor)
            close_connection(conn)
            return retv


    def get_all_tables(self,):
        retv = {'errno':0, 'msg':'', 'value':[]}
        c = self.common
        tbs = []
        if len(c.tb_list) > 0:
            for tb in c.tb_list:
                tbs.append((c.db_list[0], tb))
            retv['value'] = tbs
            return retv

        ret = self.get_all_dbs()
        db_list = ret['value']
        
        for db in db_list:
            ret = self.get_tables_by_db(db)
            if ret['errno']:
                retv['errno'] = ret['errno']
                retv['msg'] = ret['msg']
                break
            tb_tmp = ret['value']
            for tb in tb_tmp:
                tbs.append((db, tb))
        retv['value'] = tbs
        return retv

    # Check the table's PK info
    def check_primarykey(self, db, tb_list):
        c = self.common
        conn = cursor = None
        flag = 0
        try:
            logger_u.info("====Check_PK_in_%s====" % db)
            ret = connect(host=opts.host, db=db, port=opts.port)
            if ret['errno']:
                logger_u.error("connect(%s:%s) failed:%s" % \
                               (opts.host, opts.port, ret['errmsg']))
                return
            conn = ret['value']
            cursor = conn.cursor()
            #if the tb isn't exists, we should check it first
            cursor.execute("show tables")
            ans = cursor.fetchall()
            tbs = []
            tb = None
            for item in ans:
                tbs.append(item[0])
            for tb in tb_list:
                if tb not in tbs:
                    logger_u.error("%s not exists in %s" % (tb, db))
                    continue
                cursor.execute("select column_name from information_schema.\
                     STATISTICS where table_schema='%s' and table_name='%s'\
                     and index_name='primary' order by seq_in_index" % (db, tb))
                tmp_cols = cursor.fetchall()
                pk_cols = []
                pk_type = []
                for col in tmp_cols:
                    pk_cols.append(col[0]) 
                cmd = "select data_type from information_schema.columns where\
                      table_name='%s' and table_schema='%s' and column_name in\
                      ('##@@##pseudo-col'" % (tb, db)
                for i in pk_cols:
                    cmd += ", '%s'" % i
                cmd += ")"
                cursor.execute(cmd)
                res = cursor.fetchall()
                for i in res:
                    pk_type.append(str(i[0]))

                pk = '('
                if len(pk_cols) == 0:
                    logger_u.info("Table %s.%s not setting PK" % (db, tb))
                else:
                    for col in pk_cols:
                        pk += col+','
                    pk = pk[0:-1]
                    pk += ')'
                    logger_u.info("Table %s.%s's PK is %s %s" % \
                             (db, tb, pk, pk_type))
            logger_u.info("")

        except Exception, err:
            logger_s.error(str(err))
            logger_u.error('Failed: %s' % str(err))
        finally:
            close_cursor(cursor)
            close_connection(conn)
     
    # Check table's engine
    def check_store_engine(self, db, tb_list):
        c = self.common
        try:
            logger_u.info("====Check_engine_in_%s====" % db)
            for tb in tb_list:
                ret = c.get_engine(db, tb)
                if ret['errno'] == 0:
                    logger_u.info("Table %s.%s's Engine is %s" % \
                                 (db, tb, ret['value']))
                else:
                    logger_u.error(ret['msg'])
            logger_u.info("")
        except Exception, err:
            logger_s.error(str(err))
            logger_u.error('Failed: %s' % str(err))


    # Show tables' name    
    def show_tables(self, db, tb_list):
        c = self.common
        conn = None
        cursor = None
        try:
            logger_u.info('====Tables_in_%s====' % db)
            ret = connect(host=opts.host, db=db, port=opts.port)
            if ret['errno']:
                logger_u.error("connect(%s:%s) failed" % (opts.host, opts.port))
                return
            conn = ret['value']
            cursor = conn.cursor()
            for tb in tb_list:
                cursor.execute("select table_rows from information_schema.\
                       tables where table_schema='%s' and table_name='%s'"\
                       % (db, tb))
                res = cursor.fetchall()
                if len(res) > 0:
                    rows = res[0][0]
                    logger_u.info("%s.%s %s rows" % (db, tb, str(rows)))
                else:
                    logger_u.error("%s not exists in %s" % (tb, db))
            logger_u.info("")

        except Exception, err:
            logger_s.error(str(err))
            logger_u.error('Failed: %s' % str(err))
        finally:
            close_cursor(cursor)
            close_connection(conn)

    # Show all databases    
    def show_databases(self, all_db_list):
        c = self.common
        try:
            logger_u.info('====DBs_in_%s:%s====' % (opts.host, opts.port))
            for db in all_db_list:
                logger_u.info(db)
            logger_u.info("")
        except Exception, err:
            logger_s.error(str(err))
            logger_u.error('Failed: %s' % str(err))

    def get_all_dbs(self,):
        retv = {'errno':0, 'msg':'', 'value':[]}
        c = self.common
        if len(c.db_list) > 0:
            retv['value'] = c.db_list
            return retv
        # When you are only setting a port, return []
        if not opts.host:
            #retv['errno'] = 1
            #retv['msg'] = "need setting a host"
            return retv
        dbs = []
        conn =  None
        cursor = None
        try:
            ret = connect(host=opts.host, port=opts.port)
            if ret['errno']:
                retv['errno'] = 1
                retv['msg'] = "connect(%s:%s) failed" % (opts.host, opts.port)
                return retv
            conn = ret['value']
            cursor = conn.cursor()
            cursor.execute("show databases")
            tmp_db = []
            tmp_db = cursor.fetchall()
            for db in tmp_db:
                if db[0] in db_black_list:
                    continue
                if opts.db_prefix and not db[0].startswith(opts.db_prefix):
                    continue
                dbs.append(db[0])
            retv['value'] = dbs

        except Exception, err:
            retv['errno'] = -1
            retv['msg'] = str(err)
            logger_s.error(str(err))
            logger_u.error("Failed: %s " % str(err))
        finally:
            close_cursor(cursor)
            close_connection(conn)
            return retv

                    
    # Show create table information
    def show_create_table(self, db, tb_list):
        c = self.common
        cursor = None
        conn = None
        try:
            logger_u.info("====Create_table_info in %s====" % db)
            ret = connect(host=opts.host, db=db, port=opts.port)
            if ret['errno']:
                logger_u.error("connect(%s:%s) failed" % (opts.host, opts.port))
                return
            conn = ret['value']
            cursor = conn.cursor()
            for tb in tb_list:
                cursor.execute("show create table `%s`" % (tb))
                tb_def = cursor.fetchall()[0][1]
                logger_u.info("%s;" % tb_def)

        except Exception, err:
            logger_s.error(str(err))
            logger_u.error('Failed: %s' % str(err))
        finally:
            close_cursor(cursor)
            close_connection(conn)


    # Get slave hosts via show processlist
    def get_host_by_port(self, port):
        conn = None
        host = []
        #restrict IDC to mars, maybe problem for altas
        m_ip = socket.getaddrinfo('m%si.mars.grid.sina.com.cn' % (port),None)\
               [0][4][0]
        ret = connect(host=m_ip, port=int(port))
        if ret['errno']:
            logger_u.error("connect(%s(master)) failed" % port)
            return host
        host = [(m_ip,'m'), ]
        try:
            conn = ret['value']
            cursor = conn.cursor()
            cursor.execute("show processlist")
            process = cursor.fetchall()
            #one processlist like this: (186285L, 'replica', 
            #'10.55.22.207:33550', None, 'Binlog Dump', 176698L,
            #'Has sent all binlog to slave; waiting for binlog to be updated', None)
            for p in process:
                if p[4] == "Binlog Dump":
                    host.append((p[2].split(':')[0],'s'))
        except MySQLdb.Error, err:
            logger_s.error("can't get hosts from port %s.>> %s" % port, str(err))
            logger_u.error("can't get hosts from port %s" % port)
        finally:
            close_cursor(cursor)
            close_connection(conn)
            return host

    def get_machine_hardware_type(self, host):
               #"select nm.mname from"\
               #"      nwdp_admin.node2module nm, nwdp_admin.node n"\
               #" where nm.nid=n.id and n.ip_in='%s' and nm.mname in "\
               #" ('ssd', 'fusion_io', 'flashcache')"\
               #" union "\
        SQL1 = " select nm.mname from"\
               "       dp_admin.node2module nm, dp_admin.node n"\
               " where nm.nid=n.id and n.ip_in='%s' and nm.mname in "\
               " ('ssd', 'fusion_io', 'flashcache')" % host
               #" union "\
               #" select nm.mname from"\
               #"       pdp_admin.node2module nm, pdp_admin.node n"\
               #" where nm.nid=n.id and n.ip_in='%s' and nm.mname in "\
               #" ('ssd', 'fusion_io', 'flashcache') limit 1"\

        conn = cursor = None
        ret = connect(host=H3303, port=P3303)
        if ret['errno']:
            logger_s.error(ret['errmsg'])
            return ('get hd type failed',)
        try:
            conn = ret['value']
            cursor = conn.cursor()
            cursor.execute(SQL1)
            res = cursor.fetchall()
            return (res[0][0],) if len(res) else ('sas',)
        except MySQLdb.Error, e:
            logger_s.error(str(e))
            return ('get hd type failed',)

    def format_tuple(self, li):
        retv = '('
        if isinstance(li, tuple):
            for i in range(len(li)-1):
                retv += str(li[i])+', '
            retv += str(li[len(li)-1])
        else:
            retv += str(li)
        retv += ')'
        return retv

    def get_instance_dns_info(self, host, port):
        retv = []
        db_status={0:'ignore',
                   1:'online',
                   2:'delete',
                   3:'maintain',
                   4:'unknow',
                   5:'tmpoffline'}

               #"select tc.ip_in,tb.port,ta.port_status,tb.module, "\
               #"tb.dnszone,fulldomain from nwdp_admin.nm2domain ta, "\
               #"nwdp_admin.db_domain_info tb, nwdp_admin.node tc, nwdp_admin."\
               #"node2module td where ta.dbdid=tb.id and ta.nmid = td.id and"\
               #" td.nid=tc.id and tb.port=%s and tc.ip_in='%s' union "\
        SQL1 = "select tc.ip_in,tb.port,ta."\
               "port_status,tb.module, tb.dnszone,fulldomain from dp_admin."\
               "nm2domain ta, dp_admin.db_domain_info tb, dp_admin.node tc, "\
               "dp_admin.node2module"\
               " td where ta.dbdid=tb.id and ta.nmid = td.id and td.nid=tc.id "\
               "and tb.port=%s and tc.ip_in='%s' limit 1" % \
               (port, host)

        #10.29.10.182 | 3357 |           1 | s      | orion   | 
        #s3357c.orion.grid.sina.com.cn
        ret = connect(host=H3303, port=P3303)
        if ret['errno']:
            return ('get instance failed:%s' % ret['errmsg'],)
        try:
            conn = ret['value']
            cursor = conn.cursor()
            cursor.execute(SQL1)
            res = cursor.fetchall()
            if len(res):
                dm_t = res[0][5].split('.')[0].split(str(port))[-1]
                retv = (res[0][3], db_status[res[0][2]], dm_t+'.'+res[0][4])
            else:
                retv = ('s','unknow','unknow',)
        except MySQLdb.Error, e:
            retv= ('get instance failed:%s' % str(e),)
        except Exception, e:
            retv = ()
        finally:
            return retv

    def show_slave_via_show_processlist(self, host, port, step, flag):
        # Already show
        if flag.has_key(host) and flag[host]:
            return
        prefix = "    " * step
        ret = connect(host=host, port=int(port))
        if ret['errno']:
            logger_s.error("connect(%s:%s) failed:%s" % (host,port,ret['errmsg']))
            logger_u.error("%s%-15s connect failed" % (prefix, host))
            return
        try:
            conn = ret['value']
            cursor = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
            cursor.execute("show slave status")
            repl = cursor.fetchall()
            llen = len(repl)
            m_host = repl[0]['Master_Host'] if llen else 'None'
            m_file = repl[0]['Master_Log_File'] if llen else 'None'
            io_t = repl[0]['Slave_IO_Running'] if llen else 'No'
            sql_t = repl[0]['Slave_SQL_Running'] if llen else 'No'
            sbm = repl[0]['Seconds_Behind_Master'] if llen else 'NULL'

            output = (m_host, m_file, io_t, sql_t, sbm)

            # TODO: output should be more complex when -v/-vv/-vvv
            if opts.v:
                inst_info = self.get_instance_dns_info(host, port)
                output += inst_info
                hd_info = self.get_machine_hardware_type(host)
                output += hd_info

            if opts.vv:
                # TODO:
                pass

            if opts.vvv:
                # TODO:
                pass
            output = self.format_tuple(output)
            logger_u.info('%s%-15s %s' % (prefix, host, output))

            cursor = conn.cursor()
            cursor.execute("show processlist")
            process = cursor.fetchall()
            for p in process:
                if p[4] == "Binlog Dump" and p[2]:
                    _host = p[2].split(':')[0]
                    _port = p[2].split(':')[1]
                    # Avoid slave of mytrigger, mytriggerQ
                    if _host == '127.0.0.1':
                        continue
                    flag[host] = True
                    self.show_slave_via_show_processlist(_host, port, step + 1, flag)
        except MySQLdb.Error, err:
            logger_s.error("can't get hosts from port %s.>> %s" % port, str(err))
            logger_u.error("%sget slave list failed" % (prefix, host, port))


    def show_hierarchy(self, port):
        SQL1 = "select tc.ip_in,tb.port,ta.port_status,tb.module, tb.dnszone,"\
               "fulldomain from nm2domain ta, db_domain_info tb, node tc,"\
               "node2module td where ta.dbdid=tb.id and ta.nmid = td.id and "\
               "td.nid=tc.id and tb.port= %s" % port

        ret = connect(host=H3303, port=P3303, db='dp_admin')
        if ret['errno']:
            logger_s.error('connect(%s:%s) for metadata failed:%s' % \
                          (H3303, P3303, ret['errmsg']))
            logger_u.error('connect(%s:%s) for metadata failed:%s' % \
                          (H3303, P3303, ret['errmsg']))
            return 
        mdblist = []
        try:
            # We need only try dp_amdin
            conn = ret['value']
            cursor = conn.cursor()
            cursor.execute(SQL1)
            res = cursor.fetchall()
            for rec in res:
                if rec[3] == 'm':
                    mdblist.append(rec[0])
            # If we can't get info from nwdp_admin, then we try dp_admin
           # if not len(mdblist):
           #     conn.select_db('dp_admin')
           #     cursor = conn.cursor()
           #     cursor.execute(SQL1)
           #     res = cursor.fetchall()
           #     for rec in res:
           #         if rec[3] == 'm':
           #             mdblist.append(rec[0])
           # # We try pdp_admin at last
           # if not len(mdblist):
           #     conn.select_db('pdp_admin')
           #     cursor = conn.cursor()
           #     cursor.execute(SQL1)
           #     res = cursor.fetchall()
           #     for rec in res:
           #         if rec[3] == 'm':
           #             mdblist.append(rec[0])
        except MySQLdb.Error, e:
            logger_u.error('get matadata from %s failed:%s' % (P3303, str(e)))
            return

        if not len(mdblist):
            logger_u.error('port %s not exists' % port)
            return
        flag = {}
        for host in mdblist:
            for tmp in mdblist:
                flag[tmp] = True
            flag[host] = False
            self.show_slave_via_show_processlist(host, port, 0, flag)

    def select(self, port, host, sql):
        # FIXME: show output tags with role, incident.
        conn = None
        cursor = None
        host_list = []
        # FIXME: maybe we should get this host's role from db 
        host_list.append((host, ' '))
        retv = []
        if not host:
            host_list = self.get_host_by_port(port)
        for host,role in host_list:
            try:
                ret = connect(host=host, port=port)
                if ret['errno']:
                    raise MySQLdb.Error, 'connect(%s:%s) failed' % (host, port)
                conn = ret['value']
                cursor = conn.cursor()
                cursor.execute(sql)
                tmp = cursor.fetchall()
                for item in tmp:
                    retv.append("[%s]%s:%s-->%s" % (role, host, port, str(item)))
            except Exception, err:
                logger_s.error(str(err))
                retv.append("[%s]%s:%s-->error:%s" % (role, host, port, str(err)))
            finally:
                close_cursor(cursor)
                close_connection(conn)
        return retv

    def show(self, port, host, sql):
        # FIXME: show output tags with role, incident.
        conn = None
        cursor = None
        host_list = []
        # FIXME: maybe we should get this host's role from db 
        host_list.append((host, ' '))
        retv = []
        if not host:
            host_list = self.get_host_by_port(port)
        for host, role in host_list:
            try:
                ret = connect(host=host, port=port)
                if ret['errno']:
                    raise MySQLdb.Error, 'connect(%s:%s) failed' % (host, port) 
                conn = ret['value']
                cursor = conn.cursor()
                cursor.execute(sql)
                res = cursor.fetchall()
                for item in res:
                    retv.append("[%s]%s:%s-->%s" % (role, host, port, item))
            except Exception, err:
                logger_s.error(str(err))
                retv.append("[%s]%s:%s-->error:%s" % (role, host, port, str(err)))
            finally:
                close_cursor(cursor)
                close_connection(conn)
        return retv

    def truncate(self, ):
        pass

    def delete(self, ):
        pass

    def set(self, port, host, sql):
        cursor = None
        host_list = []
        host_list.append((host, ' '))
        retv = []
        if not host:
            host_list = self.get_host_by_port(port)
        for host, role in host_list:
            try:
                ret = connect(host=host, port=port)
                if ret['errno']:
                    raise MySQLdb.Error, 'connect(%s:%s) failed' % (host, port)
                conn = ret['value']
                cursor = conn.cursor()
                cursor.execute(sql)
                retv.append("[%s]%s:%s-->%s ok" % (role, host, port, sql))
            except MySQLdb.Error, err:
                logger_s.error(str(err))
                retv.append("[%s]%s:%s-->%s failed:%s" % (role, host, port,\
                            sql, str(err)))
            finally:
                close_cursor(cursor)
                close_connection(conn)
        return retv

    def alter(self, tb_list, common):
        execmanager = ExecThreadManager(tb_list, common)
        execmanager.thread_start()

    def query(self, host, query_type, sql):
        m = self.common
        if query_type == m.T_SELECT:
            ret = self.select(opts.port, host, sql)
            for item in ret:
                logger_u.info(item)
        elif query_type == m.T_SHOW:
            ret = self.show(opts.port, host, sql)
            for item in ret:
                logger_u.info(item)
        elif query_type == m.T_TRUNCATE:
            print "does'nt support trucate syntax now!"
        elif query_type == m.T_DELETE:
            print "does'nt support delete syntax now!"
        elif query_type == m.T_SET:
            ret = self.set(opts.port, host, sql)
            for item in ret:
                logger_u.info(item)
        elif query_type == m.T_ALTER:
            ret = self.get_all_tables()
            if ret['errno']:
                logger_u.error(_errmsg)
                return -1
            self.alter(ret['value'], m)


class MySQLExecThread(threading.Thread):

    def __init__(self, db, table, cmd, common):
        threading.Thread.__init__(self)
        self.db = db
        self.table = table
        self.cmd = cmd
        self.common = common
    
    #if the query type is ALTER, then we use thread
    def run(self):
        global thread_running
        global err_cnt
        global err_msg

        c = self.common
        conn = cursor = None
        try:
            ret = connect(host=opts.host, port=opts.port, db=self.db)
            if ret['errno']:
                raise MySQLdb.Error, "connect(%s:%s) failed:%s" % \
                      (opts.host, opts.port, ret['errmsg'])
            conn = ret['value']
            cursor = conn.cursor()
            #if the cmd is to change engine, do it specially
            cmd_tmp = self.cmd
            cmd_tmp = cmd_tmp.strip()
            cmd_tmp = re.subn(' {2,}', ' ', cmd_tmp)[0]
            pat = re.compile("alter table \S{1,} (.*)", re.I)

            #if user setting a invalid alter statment, then exception happens
            type = engine = None
            type = pat.match(cmd_tmp).group(1).strip()
            type = re.subn(' {1,}', '', type)[0].split("=")

            if len(type) > 1:
                type = type[1]
                #must do optimization in here
                ret = c.get_engine(self.db, self.table)
                engine = ret['value']
                if ret['errno']:
                     logger_u.warning(errmsg + "<when get engine info>")
            if type and engine and type.upper() == engine.upper():
                logger_u.info("%s:%s %s.%s %s already is %s, skipping..." % \
                        (opts.host,opts.port, self.db, self.table, self.table, engine))
            else:
                if not opts.binlog:
                    cursor.execute("set session sql_log_bin = 0")
                ret = cursor.execute(self.cmd)
                conn.commit()
                # Very rude sleep method
                time.sleep(opts.sleep)

            global ok_cnt
            ok_cnt += 1
            logger_u.info("%s:%s execute %s... ok!" % (self.db, self.table,\
                         self.cmd))
        except Exception, err:
            errstr = "%s:%s %s.%s execute <%s> failed!>> %s" % (opts.host,\
                      opts.port, self.db, self.table, self.cmd, str(err))
            logger_u.error(errstr)
            global err_cnt
            err_cnt += 1
            err_msg.append(errstr)
        finally:
            #when thread done, should let thread_running--
            thread_mutex_lock(running_mutex)
            thread_running -= 1
            print "in exec thd id(%d)" % id(thread_running)
            thread_mutex_unlock(running_mutex)

            close_cursor(cursor)
            close_connection(conn)

    

class ExecThreadManager:
    def __init__(self, tb_list, common):
        self.tb_list = tb_list
        self.common = common 

    def mutex_init(self,):
        global running_mutex
        running_mutex = thread_mutex_init()

    def thread_start(self,):
        c = self.common
        #init thread_running mutex
        self.mutex_init()
        
        tb_total = len(self.tb_list)
        tb_left = tb_total
        tb_idx = 0
        global runned_all
        global thread_running

        if not opts.execute:
            logger_u.info(ctime() + " running mode is: --dry-run, the query"+
                         " will like this:")
        else:
            logger_u.info(ctime() + " running mode is: --execute, the query"+
                         " are these:")

        while not runned_all:
            
            if thread_running < opts.threads:
                new_thd_num = opts.threads - thread_running
                if new_thd_num > tb_left:
                    new_thd_num = tb_left
                start_idx = tb_idx
                
                for i in range(start_idx, start_idx + new_thd_num):
                    cmd = c.sql_prefix + ' `' + self.tb_list[i][1] + '` '\
                          + c.sql_suffix
                    if not opts.execute:
                        logger_u.info("%s: %s" % (self.tb_list[i][0], cmd))
                    if opts.execute:
                        conn = connect(host=opts.host,
                                       db=self.tb_list[i][0],
                                       port=opts.port)
                        thd = MySQLExecThread(self.tb_list[i][0],
                                              self.tb_list[i][1],
                                              cmd,
                                              c)
                        thd.start()

                        thread_mutex_lock(running_mutex)
                        thread_running += 1
                        print "in manager thd id(%d)" % id(thread_running)
                        thread_mutex_unlock(running_mutex)
                    tb_left -= 1
                    tb_idx += 1
            # Before next time to check thread running, we sleep 1s
            if opts.execute:
                time.sleep(1)
            # if tb_left <= 0 or not self.execute:
            if tb_left <= 0:
                runned_all = True

        if not opts.execute:
            logger_u.info(ctime() + " ended the --dry-run, if it's ok, using "
                          + "--execute to do it really!")
        else:
            logger_u.info(ctime() + " ended the --execute, to check the "\
                         "following result output")


def ctime():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())






def arg_parse():

    parse = argparse.ArgumentParser(description='Login For MySQL')
    parse.add_argument('--port', '-P', type=int, required=True,
                       help='mysql port')
    parse.add_argument('--user', '-u', default='db_admin',
                       help='mysql user name, default is *****')
    parse.add_argument('--passwd', '-p', default=mysql_passwd,
                       help='mysql user passwd, default is *****')
    parse.add_argument('--host', '-H', default='127.0.0.1',help='mysql server host')
    parse.add_argument('--dc', '-d', default='ac',help='mysql server host')
    parse.add_argument('--show_create', action='store_true', default=False,
                       help='show create table info')
    parse.add_argument('--show_table', action='store_true', default=False,
                       help='show table list that you setting')
    parse.add_argument('--show_db', action='store_true', default=False,
                       help='show table db that you setting')
    parse.add_argument('--show_engine', action='store_true', default=False,
                       help="show table's engine type")
    parse.add_argument('--show_pk', action='store_true', default=False,
                       help="show table's primary key")
    parse.add_argument('--show_hi', action='store_true', default=False,
                       help="show mysql topology, if you want see verbose info"\
                       " use -v or -vv or -vvv")
    parse.add_argument('--cmd', help="you SQL statement")
    parse.add_argument('--sleep', type=float, default=0.0,
                       help="sleep time before next thread")
    parse.add_argument('--execute', action='store_true', default=False,
                       help="really execute you command")
    parse.add_argument('--dry-run', action='store_true', default=False,
                       help="to test what will be execute, only DML statement")
    parse.add_argument('--binlog', action='store_true', default=True,
                       help="logging binlog for DML statement")
    parse.add_argument('--nobinlog', action='store_true', default=False,
                       help="*NOT* logging binlog for DML statement")
    parse.add_argument('--threads', default=1, type=int,
                       help="concurrent threads to execute you command")
    parse.add_argument('--log', help="log file name default in /tmp")
    parse.add_argument('--db_prefix', help="database prefix, ignored when"\
                       " --db_list is set")
    parse.add_argument('--tb_prefix', help="table prefix, ignored when"\
                       " --tb_prefix is set")
    parse.add_argument('--tb_list', help="specify you table list, split by ','"\
                       " when it set, --tb_prefix is ignored")
    parse.add_argument('--db_list', help="specify you database list, split by"\
                       "when it set, --db_prefix is ignored ','")
    parse.add_argument('-v', action='store_true', default=False,
                       help="verbose mode")
    parse.add_argument('-vv', action='store_true', default=False,
                       help="verbose plus mode")
    parse.add_argument('-vvv', action='store_true', default=False,
			help="verbose plus plus mode")
    parse.add_argument('--version', action='version',
                        version='%(prog)s '+ str(VERSION))


    return parse, parse.parse_args()


###################################
##main
if __name__ == '__main__':

    parser, opts = arg_parse()
    args_len=len(sys.argv)
    # Debug it or not
    try:
        MYSQLSAR_DEBUG = os.environ['MYSQLSAR_DEBUG']
    except KeyError, err:
        MYSQLSAR_DEBUG = False

    if MYSQLSAR_DEBUG:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO 
    logger_s, logger_u = getLogger(opts.log, log_level)
    if not logger_s or not logger_u:
        print "get logger instance faild!"
        sys.exit(-1)

    # The argparse module isn't perfect, we do some option confict check.
    db_host=opts.host
    db_port=opts.port
    db_dc=opts.dc
    if db_host=='127.0.0.1':
	    socket_dir_cmd='ps aux|grep -v grep |grep %s|grep mysql|grep socket'%str(db_port)
	    temp_rt=run_command(socket_dir_cmd)[0].split()
	    pt=re.compile(r'.*socket.*')
	    socket_dir=''
	    for i in temp_rt:
		if  pt.search(i):
			socket_dir=i.split('=')[1]
	    if len(socket_dir)==0:
		print "Error:get socket failed"
		sys.exit()
    mysql_dir_cmd='which mysql'
    mysql_path=run_command(mysql_dir_cmd)[0].split()
    rt={}
    if check_ip(db_host):
		db_host=db_host
    elif re.match(r'[0-9]+',db_host):
	if len(db_dc)==0:
		rt['status']=-1
		rt['result']='No idc info'
		print rt
		sys.exit()
	if db_dc not in ['ac','za']:
		rt['status']=-1
		rt['result']='No idc info'
		print rt
		sys.exit()
	db_host='db%sv.infra.bj%s.pdtv.it'%(str(db_host),db_dc) 
    else:
	rt['status']=-1
	rt['result']='IP is Invalid'
	print rt
	sys.exit()	   
    if len(mysql_path)>1:
	mysql_install_cmd='yum install -y mysql.x86_64'
        run_command(mysql_install_cmd)
	sys.exit()
    try:
	    if db_host=='127.0.0.1':
		    if len(mysql_passwd)==0:
			login_cmd='mysql -u%s   -S %s -P %s'%(mysql_user,socket_dir,str(db_port))
		    else:
			login_cmd="mysql -u%s  -p'%s' -S %s -P %s"%(mysql_user,mysql_passwd,socket_dir,str(db_port))
	    else:
			login_cmd="mysql -u%s  -p'%s' -h %s -P %s"%(mysql_user,mysql_passwd,db_host,str(db_port))

    except:
	    traceback.print_exc()
	    sys.exit()
    #run_command(login_cmd)
    if args_len<=7:
	try:
    		p=subprocess.Popen(login_cmd,shell=True)
    		stdout,stderr = p.communicate()
   		retcode = p.wait()
	except:
		#traceback.print_exc()
		sys.exit()
    if opts.tb_list and \
            (not opts.db_list or \
                    (opts.db_list and \
                    len(opts.db_list.split(',')) > 1)):
       parser.print_usage()
       logger_u.error("error: ambiguous option:when you set --tb_list, "\
                      "then you must set --db_list, and only one db")
       sys.exit(-1)

    # If --cmd, then get the SQL type
    sql_prefix = ""
    sql_suffix = ""
    sql_code = -1
    if opts.cmd:
        cmd = opts.cmd.strip()
        # Replace continuous blanks with one
        cmd = re.subn(' {2,}', ' ', cmd)[0]
        match = re.match(r"(\w+) (.+)", cmd)
        if match is None:
            logger_u.error("SQL syntax error:%s" % (cmd))
            sys.exit(-1)
        res = match.groups()
        sql_type = res[0].upper()
        sql_content = res[1]
        if sql_type == "SELECT":
            sql_code = 1
        elif sql_type == "SHOW":
            sql_code = 2
        elif sql_type == "TRUNCATE":
            sql_code = 3
        elif sql_type == "DELETE":
            sql_code = 4
        elif sql_type == "SET":
            sql_code = 5
        elif sql_type == "ALTER":
            sql_code = 6
            if not opts.host:
                logger_u.error("arguments error: missing --host/-H")
                sys.exit(-1)
        else:
            sql_code = -1
        if sql_code == -1:
            logger_u.error("SQL syntax error:%s" % cmd)
            sys.exit(-1)
        if sql_code == 6:
            pattern = re.compile("(alter +table +).+? ( *.+)", re.I)
            match = pattern.match(cmd)
            if match is None:
                logger_u.error("SQL syntax error:%s" % cmd)
                sys.exit(-1)
            sql_prefix, sql_suffix = match.group(1, 2)

    # Init the Common instance
    c = Common(sql_prefix,
               sql_suffix, 
               opts.db_list.split(',') if opts.db_list else [],
               opts.tb_list.split(',') if opts.tb_list else [])
    mq = MySQLQuery(c)

    # --cmd being setted, do it specially
    if opts.cmd:
        mq.query(opts.host, sql_code, opts.cmd)
        # If SQL type is ALTER, print result info
        if sql_code == 6 and opts.execute:
            # FIXME: should be more reliable
            while thread_running > 0:
                time.sleep(0.1)
            logger_u.info("%s success!, %s fail!" % (ok_cnt, err_cnt))
            if err_cnt > 0:
                for err in err_msg:
                    logger_u.info(err)

    # show mysql topolopy hierarchy
    if opts.show_hi and opts.port:
        mq.show_hierarchy(opts.port)

    ret = mq.get_all_dbs()
    if ret['errno']:
        logger_u.error(ret['msg'])
        sys.exit(-1)
    db_list = ret['value']
    tb_list = opts.tb_list.split(',') if opts.tb_list else []
    tb_list_empty = False
    if len(tb_list) == 0:
        tb_list_empty = True

    # show databases
    if opts.show_db and opts.host:
        mq.show_databases(db_list)
    
    # show tables
    if opts.show_table and opts.host:
        for db in db_list:
            ret = mq.get_tables_by_db(db)
            if ret['errno']:
                logger_u.error(ret['msg'])
                break
            tb_list = ret['value']
            mq.show_tables(db, tb_list)
            if tb_list_empty:
                tb_list = []
    
    # show create table info
    if opts.show_create and opts.host:
        for db in db_list:
            ret = mq.get_tables_by_db(db)
            if ret['errno']:
                logger_u.error(ret['msg'])
                break
            tb_list = ret['value']
            mq.show_create_table(db, tb_list)
            if tb_list_empty:
                tb_list = []

    # show table's storage engine info
    if opts.show_engine and opts.host:
        for db in db_list:
            ret = mq.get_tables_by_db(db)
            if ret['errno']:
                logger_u.error(ret['msg'])
                break
            tb_list = ret['value']
            mq.check_store_engine(db, tb_list)
            if tb_list_empty:
                tb_list = []

    # show table's primary key info
    if opts.show_pk and opts.host:
        for db in db_list:
            ret = mq.get_tables_by_db(db)
            if ret['errno']:
                logger_u.error(ret['msg'])
                break
            tb_list = ret['value']
            mq.check_primarykey(db, tb_list)
            if tb_list_empty:
                tb_list = []


##end main
