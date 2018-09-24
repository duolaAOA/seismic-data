# -*-coding:utf-8 -*-

# 日志地址
LOG_PATH = '/data/log/'

COOKIES = {"Cookie": ""}

LOGIN_URL_COM = "https://weibo.com"

# 关键词搜索入口
TOPIC_BASE_URL = "http://s.weibo.com/apps/{topic}&pagetype=topic&topic=1&page={page}"
# 关键词详细内容入口
TOPIC_DETAIL_URL = "https://s.weibo.com/weibo/{keyword}"

# 关键词存储文件名
DATA_DIR = "/data/"
TOPIC_FILE_NAME = DATA_DIR + 'weibo/all_topics.txt'
# 关键词
TOPIC_KEYWORD = "九寨沟地震"
# 关键词提取最大页
TOPIC_MAX_PAGE = 23
# 微博话题excel文件保存路径
TOPIC_EXCEL_PATH = DATA_DIR + 'excel/'

