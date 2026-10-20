# -*- coding: utf-8 -*-
"""
Author: 章豹
Date: 2026/7/6 17:30
LastEditors: Do not edit
LastEditTime: 2026/7/6 17:30
"""
from playwright.sync_api import expect
from pages.login_page import LoginPage
import pytest


@pytest.mark.skip(reason="登录测试用例跳过")
def test_login_with_po(page, host):
    login_page = LoginPage(page)
    login_page.login(host=host)
    expect(page.locator("text=yunwei2")).to_be_visible(timeout=5000)  
        
    