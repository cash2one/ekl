#!/usr/bin/env python
# -*- encoding: UTF-8 -*-
import logging
import os

import config


conf = config.get_config()
has_inited = False
__all__ = ['get_logger']


def __init_logger(log_path):
    global conf

    fmt = '%(levelname)s %(asctime)s %(filename)s|%(lineno)d %(message)s'
    formatter = logging.Formatter(fmt)
    # conan
    conan_filename = os.path.join(log_path, conf.get('log', 'ekl_file'))
    conan_file_handler = logging.FileHandler(conan_filename, 'a')
    conan_file_handler.setLevel(logging.INFO)
    conan_file_handler.setFormatter(formatter)
    conan_logger = logging.getLogger('ekl')
    conan_logger.addHandler(conan_file_handler)
    conan_logger.setLevel(logging.INFO)
    # root
    root_filename = os.path.join(log_path, conf.get('log', 'root_file'))
    root_file_handler = logging.FileHandler(root_filename, 'a')
    root_file_handler.setLevel(logging.WARNING)
    root_file_handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    root_logger.addHandler(root_file_handler)
    root_logger.setLevel(logging.INFO)


def __init_all():
    global conf, has_inited

    abs_path = os.path.abspath(os.path.dirname(__file__))
    # 根目录
    abs_root_path = os.path.join(abs_path, '../../')
    # log 目录
    log_path = conf.get('log', 'dir')
    log_path = os.path.join(abs_root_path, log_path)
    # 如果目录不存在就建立
    if not os.path.exists(log_path):
        os.mkdir(log_path)
    # 初始化各种 logger
    __init_logger(log_path)
    has_inited = True


def get_logger(name=None):
    global has_inited

    if not has_inited:
        __init_all()

    return logging.getLogger(name)


if __name__ == '__main__':
    conan_logger = get_logger('conan')
    conan_logger.info("haha")
    root_logger = get_logger()
    root_logger.info("aaa")
    root_logger.warning("mmm")
