# -*- coding: utf-8 -*-
"""
Author: 章豹
Date: 2026-10-21
LastEditors: Do not edit
LastEditTime: 2026-10-23

采购货物认领页面对象
"""
import time
from utils.log_print import get_logger
from utils.save_screenshot import save_screenshot
from pages.public_operation import clear_el_select
from pages.base_settlement_page import BaseSettlementPage

logger = get_logger()


class PurchaseClaimPage(BaseSettlementPage):
    """采购货物认领页面"""

    def __init__(self, page):
        super().__init__(page)

        # ===== 结算 tab：收发货按钮 → 采购货物认领 =====
        self.receive_dispatch_btn = page.locator("button").filter(has_text="收发货")
        self.purchase_claim_menu_item = page.locator(
            ".el-dropdown-menu__item, [role='menuitem'], .el-popper .el-dropdown-menu__item"
        ).filter(has_text="采购货物认领")

        # ===== 结算批次表格区域 =====
        self.add_data_btn = page.locator("button:has-text('添加数据')")

    def select_purchase_claim(self):
        """步骤3：点击收发货 → 选择采购货物认领"""
        logger.info("下拉: 点击'收发货'按钮")
        self.receive_dispatch_btn.click()
        time.sleep(1)

        logger.info("下拉: 选择'采购货物认领'")
        self.purchase_claim_menu_item.wait_for(state="visible", timeout=8000)
        self.purchase_claim_menu_item.click()
        logger.info("下拉: 已选择采购货物认领，等待表格加载...")
        self.page.wait_for_timeout(5000)

    def select_batch(self, contract_code):
        """步骤4：勾选结算批次（通过 rowid 匹配合同号）"""
        code = str(contract_code)
        logger.info(f"批次: 通过 rowid 匹配合同号 {code}")

        checkbox_td = self.page.locator(f'td.col--checkbox:has([rowid*="{code}"])')
        checkbox_td.wait_for(state="attached", timeout=20000)
        logger.info("批次: 找到匹配的 td 元素")

        checkbox_td.scroll_into_view_if_needed(timeout=5000)
        self.page.wait_for_timeout(500)
        checkbox_td.click()
        self.page.wait_for_timeout(1500)
        logger.info("批次: 已勾选")

    def open_pool(self):
        """步骤5：点击添加数据，打开货权池"""
        logger.info("货权池: 点击'添加数据'")
        self.add_data_btn.click()
        time.sleep(2)

    def search_pool(self):
        """步骤6：货权池弹窗 → 清空仓库 → 搜索 → 勾选第一条"""
        dialog = self.page.locator('div.el-dialog').last
        dialog.wait_for(state="visible", timeout=15000)

        # 清空仓库
        warehouse_select = dialog.locator(
            ".el-form-item__label:has-text('仓库')"
        ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]").locator(".el-select").first
        warehouse_select.wait_for(state="visible", timeout=8000)
        clear_el_select(self.page, warehouse_select, desc="货权池-仓库")

        # 搜索
        logger.info("货权池: 点击'搜索'")
        dialog.locator("button:has-text('搜索')").click()
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
        """步骤8：配货重量=2，数量=0，是否补单=否"""
        number_inputs = self.page.locator(".el-dialog input[type='number']:visible")

        logger.info("配货: 重量=2")
        weight_input = number_inputs.nth(0)
        weight_input.wait_for(state="visible", timeout=8000)
        weight_input.fill("2")
        self.page.wait_for_timeout(300)

        logger.info("配货: 数量=0")
        qty_input = number_inputs.nth(1)
        qty_input.wait_for(state="visible", timeout=5000)
        qty_input.fill("0")
        self.page.wait_for_timeout(300)

        # 是否补单=否
        logger.info("配货: 是否补单=否")
        self.page.locator(".el-dialog .el-radio:has(input[value='0'])").first.click()
        self.page.wait_for_timeout(300)

    def save(self):
        """步骤9：保存→确定，返回是否成功"""
        dialog = self.page.locator('.el-dialog').last

        logger.info("保存: 点击'保存'")
        save_btn = dialog.locator(".el-dialog__footer button:has-text('保存')")
        save_btn.click()
        self.page.wait_for_timeout(2000)

        logger.info("保存: 点击'确定'")
        confirm_btn = self.page.locator('.el-dialog').last.locator(".el-dialog__footer button:has-text('确定')")
        confirm_btn.click()

        success = False
        try:
            ok_tip = self.page.locator("[class*='message'], [class*='toast'], [class*='notification'], [class*='tip']").filter(has_text="ok")
            ok_tip.first.wait_for(state="visible", timeout=8000)
            success = True
            logger.info("保存: 成功提示已出现")
        except Exception:
            logger.info("保存: 快速检测未捕获到提示，继续等待弹窗关闭")

        if not success:
            try:
                dialog.wait_for(state="hidden", timeout=15000)
                logger.info("保存: 弹窗已关闭")
                try:
                    ok_tip = self.page.locator("[class*='message'], [class*='toast'], [class*='notification'], [class*='tip']").filter(has_text="ok")
                    ok_tip.first.wait_for(state="visible", timeout=3000)
                    success = True
                    logger.info("保存: 成功提示已出现")
                except Exception:
                    success = True
                    logger.info("保存: 弹窗已关闭，视为保存成功")
            except Exception:
                logger.warning("保存: 弹窗未在15秒内关闭")
        return success

    def execute_purchase_claim(self, contract_code):
        """执行完整的采购货物认领流程"""
        steps = [
            ("01_navigate", lambda: self.navigate_and_search(contract_code)),
            ("02_switch_tab", lambda: self.switch_to_settlement_tab()),
            ("03_select_claim", lambda: self.select_purchase_claim()),
            ("04_select_batch", lambda: self.select_batch(contract_code)),
            ("05_open_pool", lambda: self.open_pool()),
            ("06_search_pool", lambda: self.search_pool()),
            ("07_confirm_pool", lambda: self.confirm_pool()),
            ("08_fill_details", lambda: self.fill_details()),
            ("09_save", lambda: self.save()),
        ]
        save_result = None
        for step_name, step_fn in steps:
            save_result = self._execute_step(step_name, step_fn)
        return save_result
