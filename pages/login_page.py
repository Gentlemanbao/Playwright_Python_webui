# -*- coding: utf-8 -*-
"""
@Time ： 2026/7/6 17:30
@Auth ： 章豹
@File ：login_page.py
@IDE ：PyCharm
@LastEditTime ： 2026/9/16 17:10
"""

import os
from utils.encrypt import decrypt
from utils.read_yaml import ReadConfig
from utils.log_print import get_logger

logger = get_logger()


class LoginPage:
    def __init__(self, page):
        self.page = page
        # 登录表单元素 (Vue Vben Admin)
        self.username_input = page.locator("[name='username']")
        self.password_input = page.locator("[name='password']")
        # 登录按钮：W-full 宽度100% 是登录按钮独有的 class
        self.login_button = page.locator("button.w-full:has-text('登录')")
        # 配置文件路径
        self.file_path = os.path.dirname(__file__).split(sep="pages")
        read = ReadConfig(self.file_path[0] + "/config/qx_environment.yml")
        self.psw = read.read_data("password")
        self.login_name = read.read_data("username")
        self.key = read.read_data("key")

    def login(self, username=None, password=None, host='test'):
        """
        登录方法
        :param username: 用户名，默认读取配置文件
        :param password: 密码，默认读取配置文件解密
        :param host: 环境标识 test/uat/dev
        """
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
        url = f"http://{host}/"
        logger.info(f"当前登录URL为{url}")

        self.page.goto(url, wait_until="domcontentloaded")
        # 等待登录表单出现
        self.username_input.wait_for(state="visible", timeout=15000)
        self.username_input.fill(username)
        self.password_input.fill(password)
        # Vue 登录表单需要用 Enter 键提交（click 可能被 overlay 拦截）
        self.password_input.press("Enter")
        # 等待登录成功跳转到首页
        self.page.wait_for_url("**/welcome**", timeout=20000)
        logger.info("登录成功，已跳转到首页")
