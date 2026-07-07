# -*- coding: utf-8 -*-
"""
@Time ： 2026/7/6 17:30
@Auth ： 章豹
@File ：log_print.py
@IDE ：PyCharm
@LastEditTime ： 2026/7/6 17:30
"""
import logging
import logging.handlers
from datetime import datetime
import os


def get_logger():
    logger = logging.getLogger('mylogger')  # mylogger为日志器的名称标识，如果不提供该参数，默认为'root'
    logger.setLevel(logging.DEBUG)  # 设置logger处理等级

    # 这里进行判断，如果logger.handlers列表为空，则添加，否则，直接去写日志
    if not logger.handlers:
        date = datetime.now().strftime("%Y-%m-%d") + '.log'
        log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs', date)
        # 设置输出日志格式
        f_formatter = logging.Formatter(
            '[%(asctime)s.%(msecs)03d] %(filename)s -> %(funcName)s line:%(lineno)d [%(levelname)s] : %('
            'message)s')
        fh = logging.FileHandler(log_path, encoding="utf-8")
        # 设置handler的输出等级
        fh.setLevel(logging.INFO)
        # 设置handler的输出格式
        fh.setFormatter(f_formatter)
        # 把handler添加到记录器
        logger.addHandler(fh)
        # 创建一个输出log信息到控制台的StreamHandler
        sh = logging.StreamHandler()
        sh.setLevel(logging.INFO)
        sh.setFormatter(f_formatter)
        # 把这个处理器也添加到记录器中，一个记录器可以存在多个处理器，这样log文件记录的同时屏幕也会输出log信息
        logger.addHandler(sh)

    return logger



