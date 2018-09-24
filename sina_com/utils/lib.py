#!/usr/bin/env python3
# encoding=utf-8


import re


def extract_digit(extract_task):
    """
    提取数字
    :return:    digit
    """
    d = re.search("\d+", extract_task)
    if d:
        return d.group()
    return '0'
