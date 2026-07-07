"""
Author: 章豹
Date: 2026-07-07 13:10:41
LastEditors: Do not edit
LastEditTime: 2026-07-07 14:17:12
FilePath: goods_transfer_in_page.py
"""

import time
from utils.log_print import get_logger
from utils.save_screenshot import save_screenshot


class GoodsTransferInPage:
    def __init__(self, page):
        self.page = page
        self.operation_menu = page.locator("[title='货权运营']")
        self.cargo_execution_menu = page.locator("xpath=//span[text()='货权指令执行']")
        self.transfer_in_menu = page.get_by_text("入库指令", exact=True)
        self.add_transfer_in_button = page.locator("[title='新增']")
        self.putstorageway = page.locator("[value='CARGOTRANSFER']")
        self.warehouseaddressid = page.locator("//input[@id='warehouseAddressId' and not(@aria-expanded='false')]")
        self.add = page.locator("text= 新增")
        self.customerid = page.locator("[id='customerId']")
        self.confirmdate = page.locator("[id='confirmDate']")
        self.varietyid = page.locator("[id='varietyId']")
        self.categoryid = page.locator("[id='categoryId']")
        self.inputweight = page.locator("[id='inputWeight']")
        self.inputnum = page.locator("[id='inputNum']")
        self.queding = page.get_by_role("button", name="确 定")
        self.tijiao = page.locator("xpath=//span[text()='确 定']")

    def add_transfer_in(self):
        self.operation_menu.click()
        self.cargo_execution_menu.click()
        self.transfer_in_menu.click()
        self.add_transfer_in_button.click()
        self.putstorageway.click()
        self.warehouseaddressid.click()
        self.warehouseaddressid.fill("江苏银海农佳乐仓储有限公司")
        self.page.keyboard.press('Enter')
        self.add.click()
        self.customerid.click()
        self.customerid.fill("北大方正物产集团有限公司")
        self.page.keyboard.press('Enter')
        self.confirmdate.click()
        self.page.locator("text=今天").click()
        self.varietyid.click()
        self.varietyid.fill("硅铁")
        self.page.keyboard.press('Enter')
        self.categoryid.click()
        self.page.keyboard.press('ArrowDown')
        self.page.keyboard.press('Enter')
        self.inputweight.click()
        self.inputweight.fill("189")
        self.inputnum.click()
        self.page.keyboard.press('Backspace')
        self.inputnum.fill("100")
        self.page.keyboard.press('Enter')
        self.queding.click()
        self.tijiao.click()
        
