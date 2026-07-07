
# -*- coding: utf-8 -*-
"""
@Time ： 2026/7/6 17:30
@Auth ： 章豹
@File ：case_pretask.py
@IDE ：PyCharm
@LastEditTime ： 2026/7/6 17:30
"""

from utils.remove_file import RemoveFile, clear_file
import os


file_path = os.path.dirname(__file__).split(sep="utils")[0]
def pre_task():
    print("-----------------测试用例开始执行清除历史json报告以及截图----------------------")
    clear_file(file_path + r"/temp", "是") # 清理temp目录
    RemoveFile(file_path + r"/picture/screenshots").remove_file() # 清理截图目录
    RemoveFile(file_path + r"/logs").remove_time_file()  # 清理日志文件