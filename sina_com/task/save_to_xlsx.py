#!/usr/bin/env python3
# encoding=utf-8

import os

from xlsxwriter import Workbook

from sina_com.task.get_detail_topic import CrawlDetailTopic
from sina_com.utils.settings import TOPIC_EXCEL_PATH


os.chdir(TOPIC_EXCEL_PATH)


class TopicXLSX:
    """
    Topic xlsx  generator
    """

    def __init__(self):

        self.data, self.filename = self.get_data()
        self.workbook = Workbook(self.filename)
        self.worksheet = self.workbook.add_worksheet()
        self.bold = self.workbook.add_format({'bold': True})
        self.initial_head()

    def initial_head(self):
        """
        初始化表头
        """
        headings = ["nickname", "user_auth", "content", "create_time", "device",
                    "transmit_num", "comment_num", "praise_num", "user_weibo_href",
                    "gender", "signature", "followers", "fans", "weibo_num"
                    ]

        # col = 0
        # for heading in headings:
        #     self.worksheet.write(0, col, heading, self.bold)
        #     col += 1

        self.worksheet.write_row('A1', headings, self.bold)
        self.workbook.close()

    def get_data(self):
        """
        获取topic数据
        """
        topic_obj = CrawlDetailTopic()
        data, filename = topic_obj.get_topic_detail()
        return data, filename

    def write_data(self):

        self.worksheet.write_column('A2', self.data[0])
        self.worksheet.write_column('B2', self.data[1])
        self.worksheet.write_column('C2', self.data[2])
        self.worksheet.write_column('D2', self.data[3])
        self.worksheet.write_column('E2', self.data[4])
        self.worksheet.write_column('F2', self.data[5])
        self.worksheet.write_column('G2', self.data[6])
        self.worksheet.write_column('H2', self.data[7])
        self.worksheet.write_column('I2', self.data[8])
        self.worksheet.write_column('J2', self.data[9])
        self.worksheet.write_column('K2', self.data[10])
        self.worksheet.write_column('L2', self.data[11])
        self.worksheet.write_column('M2', self.data[12])
        self.worksheet.write_column('N2', self.data[13])

        self.data.clear()

    def close_xlsx(self):

        self.workbook.close()


if __name__ == '__main__':
    xlsx = TopicXLSX()
    xlsx.write_data()