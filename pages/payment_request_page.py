# -*- coding: utf-8 -*-
"""
Author: 章豹
Date: 2026-10-22
LastEditors: Do not edit
LastEditTime: 2026-10-23

付款申请页面对象
"""
import time
from datetime import datetime
from utils.log_print import get_logger
from utils.save_screenshot import save_screenshot
from pages.public_operation import select_dropdown_option, fill_date_picker
from pages.base_settlement_page import BaseSettlementPage

logger = get_logger()


class PaymentRequestPage(BaseSettlementPage):
    """付款申请页面"""

    def __init__(self, page):
        super().__init__(page)

        # ===== 结算 tab：收付款按钮 =====
        self.receive_payment_btn = page.locator("button").filter(has_text=" 收付款 ")

    def select_payment_request(self):
        """步骤3：点击收付款 → 选择付款申请"""
        self.click_dropdown_button(self.receive_payment_btn)
        self.select_dropdown_item("付款申请")

    def fill_form(self):
        """步骤4：在付款申请弹窗中填写表单"""
        dialog = self.page.locator('.el-dialog').last
        dialog.wait_for(state="visible", timeout=10000)
        logger.info("付款申请: 填写表单")

        # 客户银行账号
        logger.info("填写: 客户银行账号")
        bank_account = dialog.locator(
            ".el-form-item__label:has-text('客户银行账号')"
        ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]").locator(".el-select").first
        bank_account.wait_for(state="visible", timeout=8000)
        select_dropdown_option(self.page, bank_account, "上海市-上海市,中国光大银行股份有限公司上海分行-35500188069094023", desc="付款申请-客户银行账号")

        # 付款期限 = 当天
        today = datetime.now().strftime("%Y-%m-%d")
        logger.info(f"填写: 付款期限={today}")
        pay_deadline = dialog.locator(
            ".el-form-item__label:has-text('付款期限')"
        ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]").locator("input").first
        fill_date_picker(self.page, pay_deadline, today)

        # 付款方式 = 前TT
        logger.info("填写: 付款方式=前TT")
        pay_method = dialog.locator(
            ".el-form-item__label:has-text('付款方式')"
        ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]").locator(".el-select").first
        select_dropdown_option(self.page, pay_method, "前TT", desc="付款申请-付款方式")

        # 账户类型 = 现金账户
        logger.info("填写: 账户类型=现金账户")
        account_type = dialog.locator(
            ".el-form-item__label:has-text('账户类型')"
        ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]").locator(".el-select").first
        select_dropdown_option(self.page, account_type, "现金账户", desc="付款申请-账户类型")

        # 备注
        logger.info("填写: 备注=测试备注")
        remark = dialog.locator(
            ".el-form-item__label:has-text('备注')"
        ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]").locator("textarea, input").first
        remark.wait_for(state="visible", timeout=5000)
        remark.fill("测试备注")
        self.page.wait_for_timeout(500)
        logger.info("付款申请: 表单填写完成")

    def click_pending_payment(self):
        """步骤5：点击待付款项，选择第一条数据并确认"""
        dialog = self.page.locator('.el-dialog').last
        logger.info("付款申请: 点击'待付款项'")
        pending_btn = dialog.locator("button:has-text(' 待付款项 ')")
        pending_btn.wait_for(state="visible", timeout=5000)
        pending_btn.click()
        self.page.wait_for_timeout(2000)

        select_dialog = self.page.locator('div.el-dialog').last
        select_dialog.wait_for(state="visible", timeout=10000)
        logger.info("待付款项: 选择第一条数据")

        checkbox = select_dialog.locator("tr.vxe-body--row .vxe-cell--checkbox:visible").first
        checkbox.wait_for(state="visible", timeout=10000)
        checkbox.click()
        self.page.wait_for_timeout(800)
        logger.info("待付款项: 已勾选第一条")

        logger.info("待付款项: 点击'确认选择'")
        confirm_btn = select_dialog.locator("button:has-text('确认选择')")
        confirm_btn.wait_for(state="visible", timeout=5000)
        confirm_btn.click()
        self.page.wait_for_timeout(2000)
        logger.info("待付款项: 已点击确认选择")

    def fill_weight_and_confirm(self):
        """步骤6：向右滚动列表，在申请重量输入框输入2，点击确定"""
        dialog = self.page.locator('.el-dialog').last
        dialog.wait_for(state="visible", timeout=10000)
        logger.info("付款申请: 向右滚动列表")

        self.page.evaluate("document.querySelector('.vxe-table--body-wrapper') && (document.querySelector('.vxe-table--body-wrapper').scrollLeft = 6400)")
        self.page.wait_for_timeout(1000)

        logger.info("填写: 申请重量=2")
        editable_input = dialog.locator(".vxe-table .el-input-number .el-input__inner").first
        editable_input.wait_for(state="visible", timeout=5000)
        editable_input.click()
        editable_input.fill("")
        editable_input.fill("2")
        self.page.wait_for_timeout(500)
        logger.info("付款申请: 已填写申请重量")

        self.click_dialog_confirm(dialog)

    def execute_payment_request(self, contract_code):
        """执行完整的付款申请流程"""
        steps = [
            ("01_navigate", lambda: self.navigate_and_search(contract_code)),
            ("02_switch_tab", lambda: self.switch_to_settlement_tab()),
            ("03_select_payment", lambda: self.select_payment_request()),
            ("04_fill_form", lambda: self.fill_form()),
            ("05_pending_payment", lambda: self.click_pending_payment()),
            ("06_fill_weight_confirm", lambda: self.fill_weight_and_confirm()),
            ("07_assert", lambda: self.assert_success("付款申请")),
        ]
        result = None
        for step_name, step_fn in steps:
            result = self._execute_step(step_name, step_fn)
        return result
