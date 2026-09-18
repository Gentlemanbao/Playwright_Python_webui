"""
Author: 章豹
Date: 2026-07-07 13:10:41
LastEditors: Do not edit
LastEditTime: 2026-07-07 14:17:12
FilePath: test_goods_transfer_In.py
"""

from playwright.sync_api import expect
from pages.login_page import LoginPage
from pages.goods_transfer_in_page import GoodsTransferInPage
from utils.save_screenshot import  save_screenshot

def test_add_transfer_in(page, host):
    login_page = LoginPage(page)
    login_page.login(host=host)
    goods_transfer_in_page = GoodsTransferInPage(page)
    goods_transfer_in_page.add_transfer_in()
    # 保存成功后列表里应该有江苏银海农佳乐的入库记录
    expect(page.get_by_text("江苏银海农佳乐").first).to_be_visible(timeout=5000)
    save_screenshot(page, "入库指令创建测试用例执行完成")

    