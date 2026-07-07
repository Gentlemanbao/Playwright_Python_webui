# -*- coding: utf-8 -*-
"""
@Time ： 2026/7/6 17:30
@Auth ： 章豹
@File ：test_login.py
@IDE ：PyCharm
@LastEditTime ： 2026/7/6 17:30
"""
from playwright.sync_api import expect
from pages.login_page import LoginPage
import pytest


@pytest.mark.skip(reason="登录测试用例跳过")
def test_login_with_po(page, host):
    login_page = LoginPage(page)
    login_page.login(host=host)
    expect(page.locator("text=yunwei2")).to_be_visible(timeout=5000)  
        
    