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