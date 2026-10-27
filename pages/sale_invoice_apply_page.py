'''
Author: 章豹
Date: 2026-10-27 10:01:53
LastEditors: Do not edit
LastEditTime: 2026-10-27 10:05:39
'''
# -*- coding: utf-8 -*-
"""
Author: 章豹
Date: 2026-10-27

销售申请开票页面对象
覆盖：合同管理→合同簿记→搜索合同→结tab→收发票→销售申请开票→填表提交→断言ok
"""
import time
from utils.log_print import get_logger
from utils.save_screenshot import save_screenshot
from pages.base_settlement_page import BaseSettlementPage

logger = get_logger()


class SaleInvoiceApplyPage(BaseSettlementPage):
    """销售申请开票页面，继承 BaseSettlementPage 复用公共入口操作"""

    def __init__(self, page):
        super().__init__(page)

        # ===== 收发票下拉按钮 =====
        self.invoice_btn = page.locator("button").filter(has_text="收发票 ")

    def select_sale_invoice_apply(self):
        """点击收发票下拉框，选择销售申请开票"""
        self.click_dropdown_button(self.invoice_btn)
        self.select_dropdown_item("销售申请开票")

    def fill_and_submit(self):
        """
        在销售申请开票弹窗中：
        1. 修改申请开票重量为 2
        2. 输入发票备注"测试申请开票"
        3. 点击确定
        4. 断言 ok
        """
        dialog = self.page.locator('.el-dialog').last
        dialog.wait_for(state="visible", timeout=10000)

        # === 1. 修改申请开票重量 ===
        logger.info("弹窗: 修改申请开票重量为 2")
        # 申请开票重量是 type="number" role="spinbutton" 的输入框
        weight_input = dialog.locator("input[role='spinbutton']").first
        weight_input.wait_for(state="attached", timeout=5000)
        weight_input.click()
        weight_input.fill("")
        weight_input.fill("2")
        self.page.wait_for_timeout(500)
        logger.info("弹窗: 申请开票重量已改为 2")

        # === 2. 输入发票备注 ===
        logger.info("弹窗: 输入发票备注'测试申请开票'")
        remark_form_item = dialog.locator(".el-form-item__label:has-text('发票备注')").locator(
            "xpath=ancestor::div[contains(@class,'el-form-item')]"
        )
        remark_input = remark_form_item.locator("input")
        remark_input.wait_for(state="attached", timeout=5000)
        remark_input.click()
        remark_input.fill("测试申请开票")
        self.page.wait_for_timeout(500)
        logger.info("弹窗: 已输入发票备注")

        # === 3. 点击确定 ===
        self.click_dialog_confirm(dialog)

        # === 4. 断言 ok ===
        self.assert_success("销售申请开票")

    def execute_full_apply(self, contract_code):
        """执行完整的销售申请开票流程"""
        steps = [
            ("01_navigate_search", lambda: self.navigate_and_search(contract_code)),
            ("02_switch_settlement_tab", lambda: self.switch_to_settlement_tab()),
            ("03_select_invoice_apply", lambda: self.select_sale_invoice_apply()),
            ("04_fill_submit", lambda: self.fill_and_submit()),
        ]
        for step_name, step_fn in steps:
            self._execute_step(step_name, step_fn)
        return True
