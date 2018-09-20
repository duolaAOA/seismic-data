# -*-coding:utf-8 -*-

# 数据库名
DB_NAME = "weibo_topic"
# 数据表名
TABLE_NAME = "topic"
# 数据库地址
HOST_NAME = '127.0.0.1'
# 数据库用户名
DATABASE_USER = 'root'
# 数据库密码
DATABASE_PASSWD = '1219960386'
# 端口
PORT = 3306
# 日志地址
LOG_PATH = '/data/log/'


LOGIN_URL_COM = "https://weibo.com"

# 关键词搜索入口
TOPIC_BASE_URL = "http://s.weibo.com/apps/{topic}&pagetype=topic&topic=1&page={page}"
# 关键词详细内容入口
TOPIC_DETAIL_URL = "http://s.weibo.com/"

# 关键词存储文件名
DATA_DIR = "/data/"
TOPIC_FILE_NAME = DATA_DIR + 'weibo/all_topics.txt'
# 关键词
TOPIC_KEYWORD = "九寨沟地震"
# 关键词提取最大页
TOPIC_MAX_PAGE = 23


