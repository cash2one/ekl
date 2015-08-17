#!/usr/bin/env python
# -*- encoding: UTF-8 -*-
import MySQLdb
import time
import config

conf = config.get_config()

# 默认状态, 还没选
ST_DEFAULT = 0
# 选中
ST_SELECTED = 1
# 剔除
ST_DELETED = 2

__all__ = ['Database', 'ST_DEFAULT', 'ST_SELECTED']


class Database(object):

    def __init__(self):
        self.__conn = None
        self.__words_table = conf.get('database', 'words_table_name')
        self.__categories_table = conf.get('database', 'categories_table_name')

    def __del__(self):
        if self.__conn:
            self.__conn.close()

    def connect(self):
        '''创立数据库连接
        '''
        # 如果连接存在就先干掉
        if self.__conn:
            self.__conn.close()

        self.__conn = MySQLdb.connect(
            host=conf.get('database', 'host'),
            port=conf.getint('database', 'port'),
            user=conf.get('database', 'user'),
            passwd=conf.get('database', 'password'),
            db=conf.get('database', 'dbname'),
        )

    def create_words_table(self):
        '''创建词条表格

        返回:
            返回成功与否
        '''
        ret = None
        with self.__conn:
            cur = self.__conn.cursor()
            sql = """CREATE TABLE IF NOT EXISTS `{table}` (
                `word` VARCHAR(255) NOT NULL,
                `cid` INT(11) NOT NULL,
                `status` INT(11) NOT NULL,
                `db_time` DOUBLE(20, 6) NOT NULL,
                INDEX word_cid_status (`word`, `cid`, `status`)
                )""".format(table=self.__words_table)
            ret = cur.execute(sql)

        if ret is None:
            return False
        return True

    def create_categories_table(self):
        '''创建分类表格

        返回:
            返回成功与否
        '''
        ret = None
        with self.__conn:
            cur = self.__conn.cursor()
            sql = """CREATE TABLE IF NOT EXISTS `{table}` (
                `cid` INT(11) NOT NULL PRIMARY KEY,
                `category` VARCHAR(255) NOT NULL
                )""".format(table=self.__categories_table)
            ret = cur.execute(sql)

        if ret is None:
            return False
        return True

    def add_word(self, word, cid):
        '''添加一个新的词条, 会自动去重

        参数:
            word: 词条
            cid: 分类 ID

        返回:
            返回成功与否
        '''
        ret = None
        with self.__conn:
            cur = self.__conn.cursor()
            sql = """INSERT INTO `{table}`
                (`word`, `cid`, `status`, `db_time`)
                SELECT '{word}', {cid}, {status}, {db_time}
                FROM DUAL WHERE NOT EXISTS
                (SELECT * FROM `{table}` WHERE `word`='{word}'
                AND `cid`={cid})""".format(
                    table=self.__words_table,
                    word=word,
                    cid=cid,
                    status=ST_DEFAULT,
                    db_time=time.time(),
                )
            ret = cur.execute(sql)

        if ret is None:
            return False
        return True

    def update_word(self, word, cid, status):
        '''更新词条的状态

        参数:
            word: 词条
            cid: 分类 ID
            status: 状态号

        返回:
            返回成功与否
        '''
        ret = None
        with self.__conn:
            cur = self.__conn.cursor()
            sql = """UPDATE `{table}`
            SET `status`={status}
            WHERE `word`='{word}' AND `cid`={cid}""".format(
                table=self.__words_table,
                word=word,
                cid=cid,
                status=status,
            )
            ret = cur.execute(sql)

        if ret is None:
            return False
        return True

    def get_words(self, cid, status, limit, skip):
        ret = None
        with self.__conn:
            cur = self.__conn.cursor()
            condition = []
            if cid is not None:
                condition.append('`cid`={}'.format(cid))
            if status is not None:
                condition.append('`status`={}'.format(status))
            if len(condition) > 0:
                condition = ' WHERE ' + ' AND '.join(condition)
            else:
                condition = ''

            sql = """SELECT * FROM `{table}`
            {condition} ORDER BY `db_time` DESC
            LIMIT {skip}, {limit}""".format(
                table=self.__words_table,
                condition=condition,
                skip=skip,
                limit=limit,
            )
            cur.execute(sql)
            item = cur.fetchone()
            while item:
                yield item
                item = cur.fetchone()

    def words_total(self, cid, status):
        ret = None
        with self.__conn:
            cur = self.__conn.cursor()
            condition = []
            if cid is not None:
                condition.append('`cid`={}'.format(cid))
            if status is not None:
                condition.append('`status`={}'.format(status))
            if len(condition) > 0:
                condition = ' WHERE ' + ' AND '.join(condition)
            else:
                condition = ''

            sql = """SELECT COUNT(*) FROM `{table}` {condition}""".format(
                table=self.__words_table,
                condition=condition,
            )
            cur.execute(sql)
            item = cur.fetchone()
            ret = item[0]
        return ret

    def add_category(self, cid, category):
        '''添加一个新的分类, 会自动去重

        参数:
            cid: 分类 ID
            category: 分类名

        返回:
            返回成功与否
        '''
        ret = None
        with self.__conn:
            cur = self.__conn.cursor()
            sql = """INSERT INTO `{table}` (`cid`, `category`)
                SELECT {cid}, '{category}' FROM DUAL WHERE NOT EXISTS
                (SELECT * FROM `{table}` WHERE `cid`={cid})""".format(
                    table=self.__categories_table,
                    cid=cid,
                    category=category,
                )
            ret = cur.execute(sql)
            print sql

        if ret is None:
            return False
        return True

    def get_categories(self):
        ret = None
        with self.__conn:
            cur = self.__conn.cursor()
            sql = """SELECT * FROM `{table}`""".format(
                table = self.__categories_table,
            )
            cur.execute(sql)
            item = cur.fetchone()
            yield item



if __name__ == '__main__':
    db = Database()
    db.connect()
    print db.create_words_table()
    #word = 'seventh'
    #db.add_word(word, 2)
    #db.update_word(word, 2, ST_SELECTED)
    #items = db.get_words(1, None, 10, 0)
    #for item in items:
    #    print item
    #total = db.words_total(1, None)
    #print total
    print db.create_categories_table()
    #db.add_category(0, 'test')
