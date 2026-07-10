"""
Author: 章豹
Description: 新增合同测试用例
Date: 2026/7/6 17:30
LastEditTime: 2026/7/6 17:30
"""
from playwright.sync_api import expect
from playwright.sync_api._generated import Page
from pages.login_page import LoginPage
from utils.save_screenshot import  save_screenshot
from pages.create_contract_page import CreateContractPage

def test_add_contract(page, host):
    """
    新增合同
    """
    login_page = LoginPage(page)
    login_page.login(host=host)
    create_contract_page = CreateContractPage(page)
    create_contract_page.create_contract()
    locator = page.locator("#logicContractCode")
    expect(locator).not_to_have_value("")
    save_screenshot(page, "create_contract.png")
   