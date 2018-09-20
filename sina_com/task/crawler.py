#!/usr/bin/env python3
# encoding=utf-8

import random

import requests

from sina_com.utils import settings
from sina_com.utils.user_agents import agents


class Config(object):
    """settings 参数配置"""

    def __init__(self):
        self.db_name = settings.DB_NAME
        self.table_name = settings.TABLE_NAME
        self.topic_base_url = settings.TOPIC_BASE_URL
        self.topic_detail_url = settings.TOPIC_DETAIL_URL
        self.topic_keyword = settings.TOPIC_KEYWORD
        self.topic_max_page = settings.TOPIC_MAX_PAGE
        self.cookie = settings.COOKIES
        self.topics_file_name = settings.TOPIC_FILE_NAME


class Crawler(Config):

    def __init__(self):
        super(Crawler, self).__init__()

        self.headers = {
            'user-agent': random.choice(agents),
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep - alive',
            'upgrade-insecure-requests': '1'
        }

        self.session = requests.session()


