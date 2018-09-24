#!/usr/bin/env python3
# encoding=utf-8

import os
import re
import json
import random
from lxml import etree
from time import sleep
from urllib import parse
from requests.exceptions import ProxyError

from sina_com.task.crawler import Crawler
from sina_com.utils.logger import Logger
from sina_com.utils import lib, settings
from sina_com.utils.user_agents import agents


log_name = os.path.basename(__file__).rsplit('.')[0]
log_path = '/data/weibo_com_log/'
log = Logger.init_logger(log_name, log_path)

# 下载过的话题记录文件
download_topic_bak = settings.DATA_DIR + "download_topic_record.txt"
# 话题文件存储路径
download_topic_path = settings.DATA_DIR + "topic_files/"
# 话题关键词
global keyword

class CrawlDetailTopic(Crawler):
    """
    抓取新浪微博关键词
    """
    crawl_record_read_finish = False
    crawl_pool = []

    def __init__(self):
        super(CrawlDetailTopic, self).__init__()
        self.count = 0
        self.next_page_pool = []

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

    def parse_detail_topic_content(self):
        """
        解析topic页面
        """

        log.info("开始获取每个话题详情！")
        for topic in self.read_local_topics():
            global keyword
            keyword = topic
            is_crawled = False
            is_crawled = self.__class__.crawl_record(topic.strip(), is_crawled)
            if is_crawled:
                log.warning("当前话题【{}】已经下载过!!!".format(topic))
                continue
            else:
                log.info("话题【{}】开始处理!".format(topic))
                self.headers["user-agent"] = random.choice(agents)
                self.next_page_pool.append(self.topic_detail_url.format(
                    keyword=parse.quote(topic.strip())))

                while self.next_page_pool is not None:

                    try:
                        html = self.session.get(
                            url=self.next_page_pool.pop(),
                            headers=self.headers,
                            cookies=self.cookie)
                    except ProxyError:
                        sleep(10)
                        log.error("话题【{}】处理失败,开始处理下一话题!!!")
                        continue

                    html.encoding = 'utf-8'

                    selector = etree.HTML(
                        bytes(bytearray(html.text, encoding='utf-8')))

                    next_page = selector.xpath('//*[@id="pl_feedlist_index"]/div[2]/div/a[@class="next"]/@href')
                    if next_page is not None:
                        self.next_page_pool.append("https:" + next_page[0])
                    else:
                        self.next_page_pool.clear()

                    all_weibo_speech = selector.xpath('//div[@action-type="feed_list_item"]')
                    yield from all_weibo_speech

    def get_topic_detail(self):
        """
        获取话题详情数据
        """
        # 昵称
        nickname = []
        # 认证
        user_auth = []
        # 用户发布内容
        content = []
        # 发送日期
        create_time = []
        # 发送设备
        device = []
        # 转发数
        transmit_num = []
        # 评论数
        comment_num = []
        # 点赞数
        praise_num = []
        # 用户微博地址
        user_weibo_href = []

        for speech in self.parse_detail_topic_content():
            nickname.extend(list(
                speech.xpath('//div[@class="card-feed"]//div[@class="content"]/div[@class="info"]/div[2]/a/@nick-name')))
            tmp_user_auth = speech.xpath('//div[@class="card-feed"]//div[@class="content"]/div[@class="info"]/div[2]')
            for i in tmp_user_auth:
                t = i.xpath('./a[2]/@title')
                if t:
                    user_auth.append(t[0])
                else:
                    user_auth.append('')

            content_lst = speech.xpath('//div[@class="card"]//div[@class="content"]/p[@node-type="feed_list_content"]')
            for i in content_lst:
                content.append(i.xpath('string(.)').strip())

            tmp_create_time = speech.xpath('//div[@class="card-feed"]//div[@class="content"]')
            for i in tmp_create_time:
                t = i.xpath('./p[last()]/a[1]/text()')
                if t:
                    create_time.append(t[0])
                else:
                    create_time.append('')

            tmp_device = speech.xpath('//div[@class="card-feed"]//div[@class="content"]')
            for i in tmp_device:
                t = i.xpath('./p[last()]/a[2]/text()')
                if t:
                    device.append(t[0])
                else:
                    device.append('')

            tmp_collections = speech.xpath('//div[@class="card"]/div[@class="card-act"]/ul')
            for i in tmp_collections:
                t = i.xpath('./li[2]/a/text()')
                if t:
                    transmit_num.append(t[0])
                else:
                    transmit_num.append(0)
            transmit_num = list(map(lib.extract_digit, transmit_num))

            for i in tmp_collections:
                t = i.xpath('./li[3]/a/text()')
                if t:
                    comment_num.append(t[0])
                else:
                    comment_num.append(0)
            comment_num = list(map(lib.extract_digit, comment_num))

            for i in tmp_collections:
                t = i.xpath('./li[4]/a/em/text()')
                if t:
                    praise_num.append(t[0])
                else:
                    praise_num.append(0)

            user_weibo_href.extend(list(speech.xpath(
                '//div[@class="card"]//div[@class="content"]/div[@class="info"]/div[2]/a[@class="name"]/@href')))

            gender, signature, followers, fans, weibo_num = self.get_user_info(user_weibo_href)

            data = [nickname, user_auth, content, create_time, device, transmit_num,
                    comment_num, praise_num, user_weibo_href, gender, signature, followers, fans, weibo_num]
            global keyword
            filename = keyword.replace("#","").strip()
            yield data, filename


    def get_user_info(self, user_info_url_lst):
        """
        获取用户详细信息

        """
        # 性别
        # W_icon icon_pf_male  男
        # W_icon icon_pf_female  女
        gender_lst = []
        # 签名
        signature_lst = []
        # 关注数
        followers_lst = []
        # 粉丝数
        fans_lst = []
        # 微博数
        weibo_num_lst = []

        for url in user_info_url_lst:
            self.headers["user-agent"] = random.choice(agents)
            try:
                html = self.session.get(
                    url="https:" + url,
                    headers=self.headers,
                    cookies=self.cookie)
            except ProxyError:
                sleep(10)
                continue

            pattern = re.compile(r'<script>FM\.view\((.*)\).*?</script>')
            html.encoding = 'utf-8'
            response = pattern.findall(html.text)
            if response:
                for i in range(len(response)):
                    strContent = response[i]

                    if '"Pl_Official_Headerv6__1"' in strContent:
                        decodejson = json.loads(strContent)
                        htmlDoc = decodejson["html"]

                        selector = etree.fromstring(htmlDoc, etree.HTMLParser(encoding='utf-8'))

                        try:
                            gender = selector.xpath(
                                '//span[@class="icon_bed"]/a/i/@class')[0]
                            if gender == 'W_icon icon_pf_male':
                                gender = 'male'
                            else:
                                gender = "female"
                        except:
                            gender = 'female'

                        try:
                            signature = selector.xpath(
                                '//div[@class="pf_intro"]/text()')[0].strip()
                        except:
                            signature = ''

                        gender_lst.append(gender)
                        signature_lst.append(signature)

                    if '"Pl_Core_T8CustomTriColumn__3"' in strContent:
                        decodejson = json.loads(strContent)
                        htmlDoc = decodejson["html"]

                        selector = etree.HTML(
                            bytes(bytearray(htmlDoc, encoding='utf-8')))

                        try:
                            followers = selector.xpath(
                                '//table[@class="tb_counter"]/tbody/tr/td[1]/strong/text()')
                            followers = followers[0]
                        except:
                            followers = 0
                        try:
                            fans = selector.xpath(
                                '//table[@class="tb_counter"]/tbody/tr/td[2]/strong/text()')
                            fans = fans[0]
                        except:
                            fans = 0
                        try:
                            weibo_num = selector.xpath(
                                '//table[@class="tb_counter"]/tbody/tr/td[3]/strong/text()')
                            weibo_num = weibo_num[0]
                        except:
                            weibo_num = 0

                        followers_lst.append(followers)
                        fans_lst.append(fans)
                        weibo_num_lst.append(weibo_num)


        return gender_lst, signature_lst, followers_lst, fans_lst, weibo_num_lst

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
    crawl.get_topic_detail()