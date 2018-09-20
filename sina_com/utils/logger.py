#!/usr/bin/env python3
# encoding=utf-8

import os
import logging
from logging import handlers

from distutils.dir_util import mkpath


# 调用时需要配置日志路径和日志名称
# LOG_PATH = '/data/order_query_log/'
# LOG_NAME = 'order_query'
# 日志等级
LOG_LEVEL = logging.DEBUG
MAX_BACK_FILE_NUM = 30
# 单个文件大小
MAX_BACK_FILE_SIZE = 256 * 1024


class Logger(object):

    @staticmethod
    def get_logger_name(log_name):
        return log_name

    @staticmethod
    def get_logger_file_name(logger_name):
        return logger_name + '.log'

    @staticmethod
    def get_or_create_log_path(log_path):
        storage_path = log_path
        if not os.path.exists(storage_path):
            mkpath(storage_path)

        return storage_path

    @staticmethod
    def get_logger_format():
        fmt = '[%(asctime)s]'
        fmt += '-[%(levelname)s]'
        fmt += '-[%(process)d]'
        fmt += '-[%(threadName)s]'
        fmt += '-[%(thread)d]'
        fmt += '-[%(filename)s:%(lineno)s]'
        fmt += ' # %(message)s'
        return fmt

    @classmethod
    def add_rotating_file_handler(cls, logger, log_path, logger_name, formatter):
        file_name = cls.get_or_create_log_path(log_path) + cls.get_logger_file_name(logger_name)
        handler = handlers.RotatingFileHandler(
            file_name,
            maxBytes=MAX_BACK_FILE_SIZE,
            backupCount=MAX_BACK_FILE_NUM,
            encoding='utf-8'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    @staticmethod
    def add_stream_handler(logger, formatter):
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    @classmethod
    def init_logger(cls, log_name, log_path, log_level=LOG_LEVEL):
        logger_name = cls.get_logger_name(log_name)
        logger = logging.getLogger(logger_name)
        formatter = logging.Formatter(cls.get_logger_format())
        cls.add_rotating_file_handler(logger, log_path, logger_name, formatter)
        cls.add_stream_handler(logger, formatter)
        logger.setLevel(log_level)
        return logger