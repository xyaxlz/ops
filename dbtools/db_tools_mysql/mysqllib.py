#! /usr/bin/python2.7
# encoding=utf-8
__author__ = 'lsj@meitu.com'

'''
Mysql base lib for connect and query action.
'''

import os
import MySQLdb

class MySQLBase(object):
    def __init__(self, host, port, user, passwd, db='', charset='', 
                 unix_socket='', use_unicode=1, connect_timeout=3, retry_times=2):
        host = '' if os.path.exists(unix_socket) is True else host
        self.__host            = host
        self.__port            = int(port)
        self.__user            = user
        self.__passwd          = passwd
        self.__db              = db
        self.__charset         = charset
        self.__unix_socket     = unix_socket
        self.__use_unicode     = use_unicode
        self.__connect_timeout = connect_timeout
        self.__retry_times     = retry_times
        self.__connection      = None

    def connection(self):
        for i in range(0, self.__retry_times+1):
            try:
                connection = MySQLdb.connect(host=self.__host, port=self.__port, user=self.__user, passwd=self.__passwd,
                                             db=self.__db, charset=self.__charset, unix_socket=self.__unix_socket, 
                                             use_unicode=self.__use_unicode, connect_timeout=self.__connect_timeout)
                break
            except Exception, e:
                if i == self.__retry_times:
                    raise e
                continue
        return connection

    def cursor(self):
        try:
            for i in range(0, self.__retry_times+1):
                if self.__connection is None:
                    self.__connection = self.connection()
                connection = self.__connection
                try:
                    cursor = connection.cursor(cursorclass=MySQLdb.cursors.DictCursor)
                    cursor.execute("set autocommit=1;")
                except MySQLdb.Error, e:
                    # retry when mysql server has gone away
                    if e[0] == 2006:
                        self.close()
                        continue
                    else:
                        raise MySQLdb.Error(e)
                return connection, cursor
        except MySQLdb.Error, e:
            raise MySQLdb.Error(e)

    def query(self, sql, fetch=True, close=True):
        try:
            connection, cursor = self.cursor()
#	    print sql
            cursor.execute(sql)
            rows = ()
            if fetch is True:
                rows = cursor.fetchall()
            if close is True:
                cursor.close()
                connection.close()
                self.__connection = None
            return rows
        except MySQLdb.Error, e:
            raise MySQLdb.Error(e)

    def close(self):
        try:
            if self.__connection:
                self.__connection.close()
                self.__connection = None
        except MySQLdb.Error, e:
            raise MySQLdb.Error(e)

def escape_string(string):
    try:
        return MySQLdb.escape_string(string)
    except Exception, e:
        raise e

if __name__ == '__main__':
    mysqlbase = MySQLBase('127.0.0.1', '3307', 'db_admin', 'BZs*gIyVeH4o0q!f')
    mysqlbase.connection()
