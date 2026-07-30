# -*- coding: utf-8 -*-
"""
@Time ： 2026/7/6 17:30
@Auth ： 章豹
@File ：login_page.py
@IDE ：PyCharm
@LastEditTime ： 2026/7/6 17:30
"""

import os
import time
from utils.encrypt import decrypt
from utils.read_yaml import ReadConfig
from utils.save_screenshot import save_screenshot
from utils.log_print import get_logger
logger = get_logger()

class LoginPage:
    def __init__(self, page):
        self.page = page
        self.username_input = page.locator("[id='username']")
        self.password_input = page.locator("[id='password']")
        self.login_button = page.locator("text=登 录")
        self.file_path = os.path.dirname(__file__).split(sep="pages")
        read = ReadConfig(self.file_path[0] + "/config/qx_environment.yml")
        self.psw = read.read_data("password")
        self.login_name = read.read_data("username")
        self.key = read.read_data("key")

    
    def login(self, username=None, password=None, host='test'):
        if username is None:
            username = self.login_name
        if password is None:
            password = decrypt(self.psw, self.key)
        url_path = "/config/qx_environment.yml"
        if host == 'uat':
            host = ReadConfig(self.file_path[0] + url_path).read_data('uat')
        elif host == 'test':
            host = ReadConfig(self.file_path[0] + url_path).read_data('test')
        else:
            host = ReadConfig(self.file_path[0] + url_path).read_data('dev')
        logger.info(f"当前环境为{host}")
        url = f"http://{host}/user/login/"
        logger.info(f"当前登录URL为{url}")
        self.page.goto(url)
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()
    