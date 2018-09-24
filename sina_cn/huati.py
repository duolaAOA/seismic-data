# -*-coding:utf-8-*-
# time:2017.06.18

import os
import re
import random
from lxml import etree
from time import sleep
from urllib import parse
from datetime import datetime

import requests
import dateparser
from pymysql.err import InternalError
from logger import Logger
from comm import settings
from comm.huati_save import get_Mysql
from comm.user_agents import agents

log_name = "topic"
log = Logger.init_logger(log_name)


class Config(object):
    """settings 参数配置"""

    def __init__(self):
        self.db_name = settings.DB_NAME
        self.table_name = settings.TABLE_NAME
        self.login_url = settings.LOGIN_URL
        self.username = settings.USERNAME
        self.password = settings.PASSWORD
        self.topic_base_url = settings.TOPIC_BASE_URL
        self.topic_keyword = settings.TOPIC_KEYWORD
        self.max_page = settings.MAX_PAGE


class FetchSinaTopic(Config):
    """
    抓取新浪微博关键词
    """

    def __init__(self):
        super(FetchSinaTopic, self).__init__()
        self.cookies = {"cookie": ""}

        self.headers = {
            'user-agent': random.choice(agents),
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep - alive',
            'upgrade-insecure-requests': '1'
        }

        self.session = requests.session()
        self.mysql = get_Mysql(self.db_name, self.table_name)
        try:
            self.mysql.create_table()
        except InternalError:
            log.warning("数据表已存在!!!")
        self.count = 0

    def fetch_topic_data(self, data_dict, start_page):
        data = data_dict
        start_page = start_page
        if start_page > 1:
            self.headers["referer"] = self.topic_base_url.format(
                parse.quote(self.topic_keyword), start_page - 1)
        else:
            self.headers["referer"] = 'https://weibo.cn/'

        html = self.session.get(
            url=self.topic_base_url.format(
                parse.quote(self.topic_keyword), start_page),
            headers=self.headers,
            cookies=self.cookies)

        while html.status_code != 200:
            #   错误重连
            log.info("错误重试, 第{}次".format(self.count + 1))
            if self.count < 3:
                sleep(3)
                self.count += 1
                return self.fetch_topic_data(data, start_page)

            else:
                pass
        else:
            self.count = 0
            sleep(0.5)
            selector = etree.fromstring(
                html.content, etree.HTMLParser(encoding='utf-8'))
            all_topic = selector.xpath(
                '//div[contains(@class,"c") and contains(@id,"M")]')

            for i in all_topic:

                # 微博发布id
                weibo_id = i.xpath('@id')[0]
                # 用户微博地址
                user_weibo_href = i.xpath('./div[1]/a[@class="nk"]/@href')[0]
                # 用户id
                user_id = re.split('/', user_weibo_href)[-1]
                # 用户发布内容
                content = i.xpath('./div[1]/span[1]')[0]
                contents = content.xpath('string(.)').replace('\u200b', '')
                # 发送日期
                time_with_device = i.xpath('./div/span[@class="ct"]/text()')[
                    0]

                html_txt = i.xpath('string(.)')
                if re.search('转发了', html_txt):
                    praise_num = int(
                        re.findall("(?<=赞\[)\d*(?=\])", html_txt)[0])
                    transmit_num = int(
                        re.findall("(?<=转发\[)\d*(?=\])", html_txt)[0])
                    comment_num = int(
                        re.findall("(?<=评论\[)\d*(?=\])", html_txt)[0])
                else:
                    praise_num = int(
                        re.findall("(?<=赞\[)\d*(?=\])", html_txt)[0])
                    transmit_num = int(
                        re.findall("(?<=转发\[)\d*(?=\])", html_txt)[0])
                    comment_num = int(
                        re.findall("(?<=评论\[)\d*(?=\])", html_txt)[0])

                try:
                    publish_time = datetime.now()
                    if re.search('月', time_with_device) and re.search(
                            '来自', time_with_device):
                        month_day, time, device = time_with_device.split(
                            maxsplit=2)
                        publish_time = dateparser.parse(
                            "18-" + month_day + ' ' + time)
                        data['device'] = device
                    elif re.search('月', time_with_device) and re.search(
                            '(\d+):(\d+)', time_with_device):
                        month_day, time = time_with_device.split(maxsplit=1)
                        publish_time = dateparser.parse(
                            "18-" + month_day + ' ' + time)
                        data['device'] = ''
                    elif re.search('今天', time_with_device) and re.search(
                            '(\d+):(\d+)', time_with_device):
                        month_day, time, device = time_with_device.split(
                            maxsplit=2)
                        publish_time = dateparser.parse(month_day + ' ' + time)
                        data['device'] = device
                    elif re.search('分钟', time_with_device) and re.search(
                            '来自', time_with_device):
                        time, device = time_with_device.split(maxsplit=1)
                        publish_time = dateparser.parse(time)
                        data['device'] = device
                    elif re.search('来自', time_with_device):
                        date, time, device = time_with_device.split(maxsplit=2)
                        publish_time = dateparser.parse(date + time)
                        data['device'] = device
                    else:
                        data['device'] = ""

                    data['create_time'] = publish_time
                except Exception as e:
                    log.error("Wrong date format!", e)

                nickname, gender, address, user_auth, signature, post_num, followers, fans = self.get_user_info(
                    user_weibo_href)
                data['weibo_id'] = weibo_id
                data['user_id'] = user_id
                data['nickname'] = nickname
                data['user_weibo_href'] = user_weibo_href
                data['gender'] = gender
                data['address'] = address
                data['user_auth'] = user_auth
                data['signature'] = signature
                data['post_num'] = post_num
                data['followers'] = followers
                data['fans'] = fans
                data['address'] = address
                data['contents'] = contents
                data['praise_num'] = praise_num
                data['transmit_num'] = transmit_num
                data['comment_num'] = comment_num
                data['comment_num'] = comment_num
                self.mysql.insert(data)

    def get_user_info(self, url):
        log.info("当前用户url为：{}".format(url))
        html = self.session.get(
            url=url, headers=self.headers, cookies=self.cookies)
        while html.status_code != 200:
            sleep(60 * 5)
            log.info("错误重试, 第{}次".format(self.count + 1))
            if self.count < 3:
                sleep(3)
                self.count += 1
                return self.get_user_info(url)

            else:
                pass
        else:
            self.count = 0
            sleep(0.5)
            selector = etree.HTML(
                bytes(bytearray(html.text, encoding='utf-8')))

            # 认证
            auth = selector.xpath(
                '//body/div[@class="u"]//div[@class="ut"]/span[1]/img')
            # 会员
            member = selector.xpath(
                '//body/div[@class="u"]//div[@class="ut"]/span[1]/a[1]/img')
            # 签名
            sign = selector.xpath(
                '//body/div[@class="u"]//div[@class="ut"]/span[2]/text()')
            # 1 无认证， 无签名， 无会员
            nickname = ''
            gender = ''
            address = ''
            user_auth = ''
            signature = ''
            if not auth and not sign and not member:
                v = selector.xpath(
                    '//body/div[@class="u"]//div[@class="ut"]/span[1]/text()')
                if v:
                    nickname_and_gender_address = v[0].split('/')
                    nickname = nickname_and_gender_address[0].split("\xa0")[0]
                    gender = nickname_and_gender_address[0].split("\xa0")[1]
                    address = nickname_and_gender_address[1].strip()
                    signature = ''
                    user_auth = ''
                else:
                    nickname = ''
                    gender = ''
                    address = ''
                    signature = ''
                    user_auth = ''

            # 2 无认证， 有签名， 无会员
            if not auth and not member and sign:
                nickname_and_gender_address = selector.xpath(
                    '//body/div[@class="u"]//div[@class="ut"]/span[1]/text()')[
                        0].split('/')
                v = nickname_and_gender_address[0].split("\xa0")
                nickname = v[0]
                gender = v[1]
                address = nickname_and_gender_address[1].split("\xa0")[
                    0].strip()
                signature = selector.xpath(
                    '//body/div[@class="u"]//div[@class="ut"]/span[2]/text()')[
                        0]
                user_auth = ''
            # 3 无认证， 有签名， 有会员
            if member and not auth and sign:
                nickname = selector.xpath(
                    '//body/div[@class="u"]//div[@class="ut"]/span[1]/text()[1]'
                )
                gender_with_address = selector.xpath(
                    '//body/div[@class="u"]//div[@class="ut"]/span[1]/text()[2]'
                )[0].split('/')
                address = gender_with_address[1]
                gender = gender_with_address[0]
                signature = selector.xpath(
                    '//body/div[@class="u"]//div[@class="ut"]/span[2]/text()')[
                        0]
                user_auth = ''
            # 4 有认证， 有签名， 无会员
            if not member and auth and sign:
                nickname = selector.xpath(
                    '//body/div[@class="u"]//div[@class="ut"]/span[1]/text()[1]'
                )[0]
                gender_with_address = selector.xpath(
                    '//body/div[@class="u"]//div[@class="ut"]/span[1]/text()[2]'
                )[0].split('/')
                address = gender_with_address[1].strip()
                gender = gender_with_address[0]
                signature = ""
                user_auth = selector.xpath(
                    '//body/div[@class="u"]//div[@class="ut"]/span[2]/text()')[
                        0]
            # 5 有认证， 有签名， 有会员
            if member and auth and sign:
                nickname = selector.xpath(
                    '//body/div[@class="u"]//div[@class="ut"]/span[1]/text()[1]'
                )[0]
                v = selector.xpath(
                    '//body/div[@class="u"]//div[@class="ut"]/span[1]/text()[2]'
                )
                gender_with_address = v[0].split('/')
                address = gender_with_address[1]
                gender = gender_with_address[0]
                user_auth = selector.xpath(
                    '//body/div[@class="u"]//div[@class="ut"]/span[2]/text()')[
                        0]
                try:
                    signature = selector.xpath(
                        '//body/div[@class="u"]//div[@class="ut"]/span[3]/text()'
                    )[0]
                except IndexError:
                    signature = ''

            try:
                post_num = re.search(
                    '\d+',
                    selector.xpath(
                        '//div[@class="tip2"]/span[@class="tc"]/text()')[
                            0]).group()
            except IndexError:
                post_num = 0
            try:
                followers = int(
                    re.search(
                        "\d+",
                        selector.xpath('//div[@class="tip2"]/a[1]/text()')[0])
                    .group())
            except IndexError:
                followers = 0
            try:
                fans = int(
                    re.search(
                        "\d+",
                        selector.xpath('//div[@class="tip2"]/a[2]/text()')[0])
                    .group())
            except IndexError:
                fans = 0

            return nickname, gender, address, user_auth, signature, post_num, followers, fans

    def insert_one(self):
        """单条插入"""
        data_dict = {}
        start_page = 1
        while start_page < self.max_page:
            data_one = self.fetch_topic_data(data_dict, start_page)
            self.mysql.insert(data_one)
            log.info('\n\n开始爬取第{}页\n\n'.format(start_page + 1))
            start_page += 1

            log.info("Crawl over!")


if __name__ == '__main__':
    crawl = FetchSinaTopic()
    crawl.insert_one()
