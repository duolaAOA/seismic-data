#!/usr/bin/env python3
# encoding=utf-8

import pymysql
import datetime
from .logger import Logger
from . import settings


log_name = "huati_save"
log_path = '/data/weibo_com_log/'
log = Logger.init_logger(log_name, log_path)


class get_Mysql(object):
    def __init__(self, db_name, table_name):
        self.db_name = db_name
        self.T = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d%H%M")
        # 数据库表格的名称
        self.table_name = '{}'.format(table_name)
        self.conn = pymysql.connect(
            host=settings.HOST_NAME,
            user=settings.DATABASE_USER,
            password=settings.DATABASE_PASSWD,
            port=settings.PORT,
            db=self.db_name,
            charset='utf8'
        )

        self.cursor = self.conn.cursor()

    def create_table(self):
        sql = ''' CREATE TABLE `{tbname}` (
                  `id` int(11) NOT NULL AUTO_INCREMENT,
                  {weibo_id} varchar(18) NOT NULL COMMENT '微博文章id',
                  {user_id} varchar(25) NOT NULL COMMENT '用户id',
                  {nickname} varchar(25) NOT NULL COMMENT '用户昵称',
                  {user_weibo_href} varchar(75) NOT NULL COMMENT '用户微博地址',
                  {gender} varchar(5) NOT NULL COMMENT '用户性别',
                  {address} varchar(20) NOT NULL COMMENT '用户所在地',
                  {user_auth} varchar(256) NOT NULL COMMENT '用户认证',
                  {signature} varchar(256) NOT NULL COMMENT '用户签名',
                  {post_num} INT(10) NOT NULL COMMENT '用户发帖数',
                  {followers} INT(10) NOT NULL COMMENT '关注',
                  {fans} INT(10) NOT NULL COMMENT '粉丝',
                  {contents} text COMMENT '微博内容',
                  {praise_num} int(10) NOT NULL COMMENT '点赞数',
                  {transmit_num} int(10) DEFAULT NULL COMMENT '转发数',
                  {comment_num} int(8) DEFAULT NULL COMMENT '评论数',
                  {device} varchar(20) DEFAULT NULL COMMENT '微博来源',
                  {create_time} timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '微博发布时间',
                  PRIMARY KEY (`id`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        '''
        try:
            self.cursor.execute(sql.format(tbname=self.table_name, weibo_id='weibo_id', user_id='user_id', nickname='nickname',
                                           user_weibo_href='user_weibo_href', gender='gender', address='address',
                                           user_auth='user_auth', signature='signature', post_num='post_num', followers='followers', fans='fans',
                                           contents='contents', praise_num='praise_num',
                                           transmit_num='transmit_num', comment_num='comment_num', device='device',
                                           create_time='create_time'))
        except Exception as e:
            log.warning('Database creation failed:', e)

        else:
            self.conn.commit()
            log.info('{} was created successfully.'.format(self.table_name))

    def insert(self, data):

        insert_sql = '''INSERT INTO `{tbname}`(weibo_id, user_id, nickname, user_weibo_href, gender, 
                                                address, user_auth, signature, post_num, followers, fans, contents, praise_num, 
                                                transmit_num, comment_num, device, create_time)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    '''
        try:
            self.cursor.execute(insert_sql.format(tbname=self.table_name),
                                (data['weibo_id'], data['user_id'], data['nickname'], data['user_weibo_href'], data['gender'],
                                 data['address'], data['user_auth'],  data['signature'], data['post_num'], data['followers'], data['fans'],
                                 data['contents'], data['praise_num'],
                                 data['transmit_num'], data['comment_num'], data['device'],
                                 data['create_time']))
        except Exception as e:
            self.conn.rollback()
            log.error('Insert the failure.：{}'.format(e))

        else:
            self.conn.commit()
            log.info('Insert a data successfully.!')

    def close_table(self):
        self.cursor.close()
        self.conn.close()


