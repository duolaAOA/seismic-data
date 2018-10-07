#!/usr/bin/env python3
# encoding=utf-8

import os

from xlsxwriter import Workbook

from sina_com.utils.settings import TOPIC_EXCEL_PATH




class TopicXLSX:

    def __init__(self, filename):

        self.workbook = Workbook(TOPIC_EXCEL_PATH + filename)
        self.worksheet = self.workbook.add_worksheet(filename)
        self.bold = self.workbook.add_format({'bold': True})
        self.index = 2
        self.initial_head()

    def initial_head(self):
        """
        初始化表头
        """
        headings = ["nickname", "user_auth", "content", "create_time", "device",
                    "transmit_num", "comment_num", "praise_num", "user_weibo_href",
                    "gender", "signature", "followers", "fans", "weibo_num"
                    ]

        self.worksheet.write_row('A1', headings, self.bold)

    def write_data(self, data):

        for i in range(0, 14):
            self.write_center(self.worksheet, (chr(65+i) + str(self.index)), data[i], self.workbook)

        self.index += len(data[0])


    @staticmethod
    def get_format_center(workbook, num=1):
        return workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'border': num
        })

    @classmethod
    def write_center(cls, worksheet, index, data, workbook):
        return worksheet.write_column(index, data, cls.get_format_center(workbook))

    def close(self):

        self.workbook.close()




