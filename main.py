# -*- coding: utf-8 -*-
"""
@Time ： 2026/7/6 17:30
@Auth ： 章豹
@File ：main.py
@IDE ：PyCharm
@LastEditTime ： 2026/7/6 17:30
"""

import os
from utils.run_edit import run_edit
from utils.case_pretask import pre_task

# 按装订区域中的绿色按钮以运行脚本。
if __name__ == '__main__':
    run_edit("test") 
    pre_task()
    os.system("pytest --alluredir ./temp")
    # os.system("pytest -n=3 --dist=loadfile --alluredir ./temp")
    os.system("allure generate ./temp -o .report --clean")
    # os.system("allure serve ./temp")


