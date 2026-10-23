# -*- coding: utf-8 -*-
"""
Author: 章豹
Date: 2026-10-22
LastEditors: Do not edit
LastEditTime: 2026-10-23

收款认领页面对象
"""
import time
from utils.log_print import get_logger
from utils.save_screenshot import save_screenshot
from pages.base_settlement_page import BaseSettlementPage

logger = get_logger()


class ReceiptClaimPage(BaseSettlementPage):
    """收款认领页面"""

    def __init__(self, page):
        super().__init__(page)

        # ===== 结算 tab：收付款按钮 =====
        self.receive_payment_btn = page.locator("button").filter(has_text=" 收付款 ")

    def select_receipt_claim(self):
        """步骤3：点击收付款 → 选择收款认领"""
        self.click_dropdown_button(self.receive_payment_btn)
        self.select_dropdown_item("收款认领")

    def click_pending_receipt(self):
        """步骤4：在收款认领弹窗中点击'待收款项'按钮"""
        dialog = self.page.locator('.el-dialog').last
        dialog.wait_for(state="visible", timeout=10000)
        logger.info("收款认领: 点击'待收款项'按钮")
        pending_btn = dialog.locator("button:has-text('待收款项')")
        pending_btn.wait_for(state="visible", timeout=5000)
        pending_btn.click()
        self.page.wait_for_timeout(2000)
        logger.info("收款认领: 已点击待收款项")

    def select_all_items(self):
        """步骤5：在待收款项选择弹窗中，勾选表头全选复选框，点击确认选择"""
        dialog = self.page.locator('div.el-dialog').last
        dialog.wait_for(state="visible", timeout=10000)
        logger.info("待收款项: 勾选表头全选复选框")
        self.page.wait_for_timeout(2000)

        header_checkbox = dialog.locator(
            "span.vxe-cell--checkbox[title='全选/取消']"
        ).first
        header_checkbox.wait_for(state="attached", timeout=10000)
        header_checkbox.click(force=True)
        self.page.wait_for_timeout(800)
        logger.info("待收款项: 已勾选全选")

        logger.info("待收款项: 点击'确认选择'")
        confirm_btn = dialog.locator("button:has-text('确认选择')")
        confirm_btn.wait_for(state="visible", timeout=5000)
        confirm_btn.click()
        self.page.wait_for_timeout(2000)
        logger.info("待收款项: 已点击确认选择")

    def confirm_claim(self):
        """步骤6：数据回显后点击确定，关闭 MessageBox"""
        self.click_dialog_confirm()
        self.close_message_box()

    def execute_receipt_claim(self, contract_code):
        """执行完整的收款认领流程"""
        steps = [
            ("01_navigate", lambda: self.navigate_and_search(contract_code)),
            ("02_switch_tab", lambda: self.switch_to_settlement_tab()),
            ("03_select_claim", lambda: self.select_receipt_claim()),
            ("04_click_pending", lambda: self.click_pending_receipt()),
            ("05_select_all", lambda: self.select_all_items()),
            ("06_confirm", lambda: self.confirm_claim()),
            ("07_assert", lambda: self.assert_success("收款认领")),
        ]
        result = None
        for step_name, step_fn in steps:
            result = self._execute_step(step_name, step_fn)
        return result
