#!/usr/bin/env python3
# encoding=utf-8


from xlsxwriter import Workbook
from sina_com.utils.settings import TOPIC_EXCEL


class TopicXLSX:
    """
    Topic xlsx  generator
    """

    def __init__(self, output_filename):
        self.workbook = Workbook(output_filename)
        self.worksheet = self.workbook.add_worksheet()
        self.bold = self.workbook.add_format({'bold': True})
        self.initial_head()

    def initial_head(self):
        """
        初始化表头
        """
        headings = ["nickname", "user_auth", "content", "create_time", "device",
                    "transmit_num", "comment_num", "praise_num", "user_weibo_href",
                    "gender", "signature", "followers""fans", "weibo_num"
                    ]

        for target_worksheet, heading in (self.worksheet, headings):
            col = 0
            target_worksheet.write(1, col, heading, self.bold)
            col += 1

        # self.worksheet.write_row('A1', headings, self.bold)

    def write_data(self, postion, data):
        self.worksheet.write_row(postion, data)

    def close_xlsx(self):

        self.workbook.close()
