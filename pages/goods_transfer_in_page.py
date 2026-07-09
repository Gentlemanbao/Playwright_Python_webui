'''
Author: 章豹
Date: 2026-07-07 13:10:41
LastEditors: Do not edit
LastEditTime: 2026-07-09 16:31:45
FilePath: \ui_auto_project\pages\goods_transfer_in_page.py
'''
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
from pages.public_operation import repetitive_operation


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
        self.inputnum = page.locator("//input[@id='inputNum' and (@value='0')]")
        self.queding = page.get_by_role("button", name="确 定")
        self.tijiao = page.locator("xpath=//span[text()='确 定']")

    def add_transfer_in(self):
        """
        新增入库指令
        """
        self.operation_menu.click()
        self.cargo_execution_menu.click()
        self.transfer_in_menu.click()
        self.add_transfer_in_button.click()
        self.putstorageway.click()
        self.warehouseaddressid.click()
        repetitive_operation(self.page, self.warehouseaddressid, "江苏银海农佳乐仓储有限公司")
        self.add.click()
        self.confirmdate.click()
        self.page.locator("text=今天").click()
        self.varietyid.click()
        repetitive_operation(self.page, self.varietyid, "硅铁")
        self.categoryid.click()
        self.page.keyboard.press('ArrowDown')
        self.page.keyboard.press('Enter')
        repetitive_operation(self.page, self.inputweight, "189")
        repetitive_operation(self.page, self.inputnum, "100")
        repetitive_operation(self.page, self.customerid, "北大方正物产集团有限公司", is_click=True)
        locator = self.page.locator("xpath=//span[text()='确 定']")
        print(locator.count())
        locator.nth(1).click()
        self.tijiao.click()
        
