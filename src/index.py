#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import tornado.ioloop
import tornado.web
import libs

conf = libs.get_config()
logger = libs.get_logger('ekl')
db = libs.Database()
db.connect()


class Add(tornado.web.RequestHandler):

    def get(self):
        # Unicode 字符
        word = self.get_argument('word', None)
        cid = self.get_argument('cid', None)
        # 因为前端是输入 UTF-8 字符, 可能引入 BOM
        # 统一起见, 去除 BOM
        word = libs.clean_bom(word).encode("utf-8")

        errno = 0
        msg = None
        if None in (word, cid) or not cid.isdigit():
            errno = 1
            msg = 'invalid_params'
        else:
            cid = int(cid)
            if db.add_word(word, cid):
                errno = 0
                msg = 'success'
            else:
                errno = 2
                msg = 'failed'

        log_string = 'errno={}, msg={}, word={}, cid={}'.format(
                     errno, msg, word, cid)
        logger.info(log_string)
        self.write(libs.compose_ret(errno, msg))


class Update(tornado.web.RequestHandler):

    def get(self):
        # Unicode 字符
        word = self.get_argument('word', None)
        cid = self.get_argument('cid', None)
        status = self.get_argument('st', None)
        # 因为前端是输入 UTF-8 字符, 可能引入 BOM
        # 统一起见, 去除 BOM
        word = libs.clean_bom(word).encode("utf-8")

        errno = 0
        msg = None
        if None in (word, cid, status) or \
                not cid.isdigit() or \
                not status.isdigit():
            errno = 1
            msg = 'invalid_params'
        else:
            cid = int(cid)
            status = int(status)
            if db.update_word(word, cid, status):
                errno = 0
                msg = 'success'
            else:
                errno = 2
                msg = 'failed'

        log_string = 'errno={}, msg={}, word={}, cid={}, status={}'.format(
                     errno, msg, word, cid, status)
        logger.info(log_string)
        self.write(libs.compose_ret(errno, msg))


class List(tornado.web.RequestHandler):
    '''可以接受如下参数 (括号中为 GET 参数):
        1. 页号         page (p)
        2. 每页条目数   line_num (ln)
        3. 类型 ID      cid (cid)
        4. 状态码       status (st)
    '''

    categories = {}
    items = db.get_categories()
    for item in items:
        cid, category = item
        categories[cid] = category

    def get(self):
        # 各种过滤参数
        # 页号 (必选)
        page = self.get_argument('p', 1)
        try:
            page = int(page)
        except:
            page = 1
        if page < 1:
            page = 1
        # 每页条目数 (必选)
        line_num = self.get_argument('ln', 10)
        try:
            line_num = int(line_num)
        except:
            line_num = 10
        if line_num < 1:
            line_num = 10
        # cid 过滤 (可选)
        cid = self.get_argument('cid', None)
        try:
            cid = int(cid)
        except:
            cid = None
        # status 过滤 (可选)
        status = self.get_argument('st', None)
        try:
            status = int(status)
        except:
            status = None

        items = db.get_words(cid, status, line_num, (page - 1) * line_num)
        data = {'header': ['词条', '类别号', ' 状态码', ' 创建时间'], 'content': []}
        for item in items:
            cid = item[1]
            item = list(item)
            item.append(self.__class__.categories[cid])
            data['content'].append(item)
        self.write(libs.compose_ret(0, data))


class Total(tornado.web.RequestHandler):

    def get(self):
        # 各种过滤参数
        # cid 过滤 (可选)
        cid = self.get_argument('cid', None)
        try:
            cid = int(cid)
        except:
            cid = None
        # status 过滤 (可选)
        status = self.get_argument('st', None)
        try:
            status = int(status)
        except:
            status = None

        total = db.words_total(cid, status)
        data = {'total': total}
        self.write(libs.compose_ret(0, data))



def start_server():
    application = tornado.web.Application([
            (r'/api/v1/add', Add),
            (r'/api/v1/list', List),
            (r'/api/v1/update', Update),
            (r'/api/v1/total', Total),
            (r'/(.*)', tornado.web.StaticFileHandler, {"path": "html"}),
        ],
        **{'debug': True}
    )
    port = conf.get('server', 'port')
    application.listen(port)
    instance = tornado.ioloop.IOLoop.instance()
    instance.start()


if __name__ == '__main__':
    start_server()
