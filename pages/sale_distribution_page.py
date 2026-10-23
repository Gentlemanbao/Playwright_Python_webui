# -*- coding: utf-8 -*-
"""
Author: 章豹
Date: 2026-10-22
LastEditors: Do not edit
LastEditTime: 2026-10-23

销售配货页面对象
"""
import time
from datetime import datetime, timedelta
from utils.log_print import get_logger
from utils.save_screenshot import save_screenshot
from pages.public_operation import select_dropdown_option, fill_date_picker, get_vxe_table_by_header, vxe_fill_cell
from pages.base_settlement_page import BaseSettlementPage

logger = get_logger()


class SaleDistributionPage(BaseSettlementPage):
    """销售配货页面"""

    def __init__(self, page):
        super().__init__(page)

        # ===== 结算 tab：收发货按钮 → 销售配货 =====
        self.receive_dispatch_btn = page.locator("button").filter(has_text="收发货")

        # ===== 销售配货弹窗 =====
        self.add_data_btn = page.locator("button:has-text('添加数据')")

    def select_sale_distribution(self):
        """步骤3：点击收发货 → 选择销售配货"""
        self.click_dropdown_button(self.receive_dispatch_btn)
        self.select_dropdown_item("销售配货")
        # 等待弹窗完全渲染（vxe-table 数据加载较慢）
        self.page.wait_for_timeout(6000)

    def select_batch(self):
        """步骤4：在销售配货弹窗左侧勾选第一条结算批次"""
        logger.info("批次: 勾选左侧第一条结算批次")
        dialog = self.page.locator('.el-dialog').last
        dialog.wait_for(state="visible", timeout=15000)
        # 等待表格数据加载完成（vxe-table body row 出现）
        self.page.wait_for_timeout(2000)
        checkbox = dialog.locator("tr.vxe-body--row .vxe-cell--checkbox:visible").first
        checkbox.wait_for(state="visible", timeout=15000)
        checkbox.scroll_into_view_if_needed(timeout=5000)
        self.page.wait_for_timeout(500)
        checkbox.click()
        self.page.wait_for_timeout(2000)
        logger.info("批次: 已勾选第一条")

    def open_pool(self):
        """步骤5：点击添加数据，打开货权池"""
        logger.info("货权池: 点击'添加数据'")
        self.add_data_btn.click()
        time.sleep(2)

    def search_pool(self):
        """步骤6：货权池弹窗 → 展开 → 选账号类型=在库 → 搜索 → 勾选第一条"""
        dialog = self.page.locator('div.el-dialog').last
        dialog.wait_for(state="visible", timeout=15000)

        # 点开展开按钮
        logger.info("货权池: 点开展开按钮")
        expand_btn = dialog.locator("button.el-button--primary.is-link:has-text('展开 ')")
        if expand_btn.count() > 0 and expand_btn.is_visible():
            expand_btn.click()
            self.page.wait_for_timeout(1000)

        # 账号类型=在库
        account_type_select = dialog.locator(
            ".el-form-item__label:has-text('账号类型')"
        ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]").locator(".el-select").first
        account_type_select.wait_for(state="visible", timeout=8000)
        select_dropdown_option(self.page, account_type_select, "在库", desc="货权池-账号类型")

        # 搜索
        logger.info("货权池: 点击搜索按钮")
        search_icon_btn = dialog.locator("button.el-button:has(.el-icon-search)")
        if search_icon_btn.count() > 0:
            search_icon_btn.first.click()
        else:
            dialog.locator("button:has(.el-icon-search), button:has-text('搜索')").first.click()
        self.page.wait_for_timeout(2000)

        # 勾选第一条
        logger.info("货权池: 勾选第一条记录")
        checkbox = dialog.locator("tr.vxe-body--row .vxe-cell--checkbox:visible").first
        checkbox.wait_for(state="visible", timeout=10000)
        checkbox.click()
        self.page.wait_for_timeout(800)
        logger.info("货权池: 第一条记录已选中")

    def confirm_pool(self):
        """步骤7：货权池弹窗确定"""
        dialog = self.page.locator('div.el-dialog').last
        logger.info("货权池: 点击'确定'")
        dialog.locator(".el-dialog__footer button:has-text('确定')").last.click()
        time.sleep(2)

    def fill_details(self):
        """步骤8：填写仓储费截止日、提单截止日、交货方式、配货重量、配货数量"""
        today = datetime.now().strftime("%Y-%m-%d")
        future = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        dialog = self.page.locator('.el-dialog').last

        # 仓储费截止日
        logger.info(f"填写: 仓储费截止日={today}")
        storage_end = dialog.locator(
            ".el-form-item__label:has-text('仓储费截止日')"
        ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]").locator("input").first
        fill_date_picker(self.page, storage_end, today)

        # 提单截止日
        logger.info(f"填写: 提单截止日={future}")
        bill_end = dialog.locator(
            ".el-form-item__label:has-text('提单截止日')"
        ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]").locator("input").first
        fill_date_picker(self.page, bill_end, future)

        # 交货方式=货转
        logger.info("填写: 交货方式=货转")
        delivery_method = dialog.locator(
            ".el-form-item__label:has-text('交货方式')"
        ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]").locator(".el-select").first
        select_dropdown_option(self.page, delivery_method, "货转", desc="销售配货-交货方式")

        # 配货重量=2
        logger.info("填写: 配货重量=2")
        table = get_vxe_table_by_header(self.page, marker_header="账号类型")
        vxe_fill_cell(self.page, table, "配货重量", "2", field_type='spinbutton')

        # 配货数量=0
        logger.info("填写: 配货数量=0")
        vxe_fill_cell(self.page, table, "配货数量", "0", field_type='spinbutton')

    def deliver_and_assert(self):
        """步骤9：点击配货出库，断言 ok"""
        logger.info("配货出库: 点击'配货出库'")
        deliver_btn = self.page.locator("button:has-text('配货出库')")
        deliver_btn.wait_for(state="visible", timeout=10000)
        deliver_btn.click()
        self.page.wait_for_timeout(2000)

        return self.assert_success("销售配货")

    def execute_sale_distribution(self, contract_code):
        """执行完整的销售配货流程"""
        steps = [
            ("01_navigate", lambda: self.navigate_and_search(contract_code)),
            ("02_switch_tab", lambda: self.switch_to_settlement_tab()),
            ("03_select_distribution", lambda: self.select_sale_distribution()),
            ("04_select_batch", lambda: self.select_batch()),
            ("05_open_pool", lambda: self.open_pool()),
            ("06_search_pool", lambda: self.search_pool()),
            ("07_confirm_pool", lambda: self.confirm_pool()),
            ("08_fill_details", lambda: self.fill_details()),
            ("09_deliver_assert", lambda: self.deliver_and_assert()),
        ]
        result = None
        for step_name, step_fn in steps:
            result = self._execute_step(step_name, step_fn)
        return result
