# -*- coding: utf-8 -*-
"""
Author: 章豹
Date: 2026/7/6 17:30
LastEditors: Do not edit
LastEditTime: 2026/10/19 16:21:27
"""

import os
import shutil
import threading
import webbrowser
from utils.run_edit import run_edit
from utils.case_pretask import pre_task




if __name__ == '__main__':
    run_edit("test")
    pre_task()
    os.system("pytest --alluredir ./temp")
    if os.path.isdir("report"):
        shutil.rmtree("report", ignore_errors=True)
    os.system("allure generate ./temp -o report --clean")
    os.system("allure serve ./temp")


