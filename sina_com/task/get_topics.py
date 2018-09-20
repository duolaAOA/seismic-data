#!/usr/bin/env python3
# encoding=utf-8

import os
import random
from lxml import etree
from time import sleep
from urllib import parse

from .crawler import Crawler
from sina_com.utils import settings
from sina_com.utils.logger import Logger
from sina_com.utils.user_agents import agents

log_name = os.path.basename(__file__).rsplit('.')[0]
log_path = settings.DATA_DIR + 'weibo_com_log/'
log = Logger.init_logger(log_name, log_path)


class FetchSinaTopic(Crawler):
    """
    抓取新浪微博关键词
    """

    def __init__(self):
        super(FetchSinaTopic, self).__init__()
        self.count = 0

    def _save_all_topic(self):
        """
        保存相关所有topic
        """
        topic_lst = []
        start_page = 1
        while start_page < self.topic_max_page:
            log.info("正在下载第{}页".format(start_page))
            topics = self.get_all_topic(start_page)
            start_page += 1
            topic_lst.extend(topics)

        if os.path.exists(self.topics_file_name):
            log.info("相关话题已经存在！！")
        else:
            with open(self.topics_file_name, 'w', encoding='utf-8') as f:
                for topic in topic_lst:
                    f.write(topic + '\n')
                log.info("相关话题下载完毕!")

    def get_all_topic(self, start_page):
        """
        获取相关所有topic
        """
        self.headers["user-agent"] = random.choice(agents)
        if start_page > 1:
            self.headers["referer"] = self.topic_base_url.format(
                topic=parse.quote(self.topic_keyword), page=start_page - 1)
        else:
            self.headers["referer"] = 'http://s.weibo.com/'

        html = self.session.get( url=self.topic_base_url.format(topic=parse.quote(self.topic_keyword), page=start_page),
                headers=self.headers,
                cookies=self.cookie)

        while html.status_code != 200:
            log.warning("连接失败，正在第{}次重连...".format(self.count + 1))
            if self.count < 5:
                sleep(10)
                self.count += 1
                return self.get_all_topic(start_page)
            else:
                self.count = 0
        else:
            self.count = 0
            sleep(0.5)
            selector = etree.fromstring(html.content, etree.HTMLParser(encoding='utf-8'))
            all_topics = selector.xpath('//div[@class="topic_content"]/div[@class="detail"]/h1/a/text()')
            if not all_topics:
                return self.get_all_topic(start_page)

            return list(all_topics)


if __name__ == '__main__':
    crawl = FetchSinaTopic()
    crawl._save_all_topic()
