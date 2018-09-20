#!/usr/bin/env python3
# encoding=utf-8

import os
import re
import random
from lxml import etree
from time import sleep
from urllib import parse
from datetime import datetime

import requests
import dateparser
from sina_com.task.crawler import Crawler
from sina_com.utils.logger import Logger
from sina_com.utils import settings
from sina_com.utils.user_agents import agents


log_name = os.path.basename(__file__).rsplit('.')[0]
log_path = '/data/weibo_com_log/'
log = Logger.init_logger(log_name, log_path)

# 下载过的话题记录文件
download_topic_bak = settings.DATA_DIR + "download_topic_record.txt"
# 话题文件存储路径
download_topic_path = settings.DATA_DIR + "topic_files/"

class CrawlDetailTopic(Crawler):
    """
    抓取新浪微博关键词
    """
    crawl_record_read_finish = False
    crawl_pool = []
    start_page = 1

    def __init__(self):
        super(CrawlDetailTopic, self).__init__()
        self.count = 0

    def read_local_topics(self):
        """
        读取本地topics文件
        """
        try:
            with open(self.topics_file_name, 'r', encoding='utf-8') as reader:
                topic_lst = reader.readlines()
        except:
            raise FileNotFoundError("文件不存在,请确认是否存在文件？")

        yield from topic_lst

    def get_detail_topic(self):
        """
        获取话题详情
        """
        # 昵称
        nickname = ''
        # 性别
        # W_icon icon_pf_male  男
        # W_icon icon_pf_female  女
        gender = ''
        # 签名
        signature = ''
        # 认证
        user_auth = ''
        # 用户微博地址
        user_weibo_href = ''
        # 关注数
        followers = 0
        # 粉丝数
        fans = 0
        # 地址
        address = ''
        # 微博数
        weibo_num = 0
        # 用户发布内容
        content = ''
        # 发送日期
        create_time = ''
        # 发送设备
        device = ''
        # 点赞数
        praise_num = ''
        # 评论数
        comment_num = ''
        # 转发数
        transmit_num = ''


        log.info("开始获取每个话题详情！")
        for topic in self.read_local_topics():
            is_crawled = False
            is_crawled = self.__class__.crawl_record(topic, is_crawled)
            if is_crawled:
                log.warning("当前话题【{}】已经下载过!!!".format(topic))
                continue
            else:
                log.info("话题【{}】开始处理!".format(topic))
                self.headers["user-agent"] = random.choice(agents)
                html = self.session.get(
                    url=(self.topic_detail_url+'weibo/{keyword}&page={page}').format(keyword=parse.quote(topic.strip()), page=self.__class__.start_page),
                    headers=self.headers,
                    cookies=self.cookie)
                html.encoding = 'utf-8'
                resp = html.text



    @classmethod
    def crawl_record(cls, topic, is_crawled):
        """
        话题抓取记录
        """
        if os.path.exists(download_topic_bak):
            if cls.crawl_record_read_finish:
                pass
            else:
                with open(download_topic_bak, 'r', encoding='utf-8') as reader:
                    for i in reader.readlines():
                        cls.crawl_pool.append(i.strip())
                cls.crawl_record_read_finish = True

        else:
            with open(download_topic_bak, 'w', encoding='utf-8') as f:
                f.write('')

        with open(download_topic_bak, 'a+', encoding='utf-8') as writer:
            if topic in cls.crawl_pool:
                is_crawled = True
                return is_crawled
            else:
                writer.write(topic + '\n')
                return is_crawled


if __name__ == "__main__":
    crawl = CrawlDetailTopic()
    crawl.get_detail_topic()