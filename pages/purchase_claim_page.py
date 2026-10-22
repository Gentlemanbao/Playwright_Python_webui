# -*- coding: utf-8 -*-
"""
Author: 章豹
Date: 2026-10-21
LastEditors: Do not edit
LastEditTime: 2026-10-21
"""

import time
from utils.log_print import get_logger
from utils.save_screenshot import save_screenshot
from pages.public_operation import clear_el_select

logger = get_logger()


class PurchaseClaimPage:
    """采购货物认领页面"""

    def __init__(self, page):
        self.page = page

        # ===== 菜单导航 =====
        self.contract_management_menu = page.locator(".vben-sub-menu:has-text('合同管理')")
        self.contract_bookkeeping_menu = page.locator(".vben-menu-item__content:has-text('合同簿记')")
        self.search_contract_input = page.locator("[placeholder='请输入合约编号']")
        self.search_btn = page.locator("button:has-text('搜索')")

        # ===== 合同详情 Tabs =====
        self.settlement_tab = page.locator(".el-tabs__item").filter(has_text="结")

        # ===== 结算 tab：收发货按钮 → 采购货物认领 =====
        self.receive_dispatch_btn = page.locator("button").filter(has_text="收发货")
        self.purchase_claim_menu_item = page.locator(
            ".el-dropdown-menu__item, [role='menuitem'], .el-popper .el-dropdown-menu__item"
        ).filter(has_text="采购货物认领")

        # ===== 结算批次表格区域 =====
        self.add_data_btn = page.locator("button:has-text('添加数据')")

    def _execute_step(self, step_name, fn):
        """执行单个步骤，报错时自动截图并抛出，返回步骤返回值"""
        try:
            return fn()
        except Exception as e:
            save_screenshot(self.page, f"失败_{step_name}")
            logger.error(f"❌ 步骤 [{step_name}] 执行失败: {e}")
            raise RuntimeError(f"步骤 [{step_name}] 失败: {e}") from e

    def navigate_and_search(self, contract_code):
        """步骤1：合同管理 → 合同簿记 → 搜索合同号"""
        logger.info("导航: 点击'合同管理'")
        self.contract_management_menu.click()
        time.sleep(0.5)

        logger.info("导航: 点击'合同簿记'")
        self.contract_bookkeeping_menu.click()
        time.sleep(2)

        code = str(contract_code)
        logger.info(f"搜索: 填入合同号 {code}")
        for i in range(3):
            self.search_contract_input.fill(code)
            time.sleep(0.5)
            if self.search_contract_input.input_value() == code:
                break
        else:
            logger.error(f"搜索: 填入'{code}'3次均被清空")

        self.search_btn.click()

        # 等待合同详情加载完成（搜索后进入详情页）
        h3 = self.page.locator("h3").first
        for i in range(60):
            try:
                if code in h3.inner_text():
                    logger.info(f"详情: 已加载，标题'{h3.inner_text()}'")
                    break
            except Exception:
                pass
            time.sleep(0.5)
        else:
            logger.warning("详情: 未检测到合同号出现在标题中，继续执行")
        logger.info("搜索: 已进入合同详情页")

    def switch_to_settlement_tab(self):
        """步骤2：切换到"结算"tab"""
        logger.info("Tab: 切换到'结算'")
        self.settlement_tab.click()
        time.sleep(2)
        logger.info("Tab: 已切换到结算")

    def select_purchase_claim(self):
        """
        步骤3：点击"收发货"按钮 → 选择"采购货物认领"
        """
        logger.info("下拉: 点击'收发货'按钮")
        self.receive_dispatch_btn.click()
        time.sleep(1)

        logger.info("下拉: 选择'采购货物认领'")
        self.purchase_claim_menu_item.wait_for(state="visible", timeout=8000)
        self.purchase_claim_menu_item.click()
        logger.info("下拉: 已选择采购货物认领，等待表格加载...")
        self.page.wait_for_timeout(5000)

    def select_batch(self, contract_code):
        """
        步骤4：勾选结算批次
        通过 rowid 匹配合同号找到对应 td 并点击（vxe-table 事件绑定在 td 上）
        """
        code = str(contract_code)
        logger.info(f"批次: 通过 rowid 匹配合同号 {code}")

        # 找到包含 rowid 匹配合同号的 td.col--checkbox（vxe-table 事件绑在 td 上）
        checkbox_td = self.page.locator(f'td.col--checkbox:has([rowid*="{code}"])')
        checkbox_td.wait_for(state="attached", timeout=20000)
        logger.info("批次: 找到匹配的 td 元素")

        # 滚动到视口
        checkbox_td.scroll_into_view_if_needed(timeout=5000)
        self.page.wait_for_timeout(500)

        # 点击 td 触发 vxe-table 的行选中事件
        checkbox_td.click()
        self.page.wait_for_timeout(1500)
        logger.info("批次: 已勾选")

    def open_pool(self):
        """步骤5：点击添加数据，打开货权池"""
        logger.info("货权池: 点击'添加数据'")
        self.add_data_btn.click()
        time.sleep(2)

    def search_pool(self):
        """步骤6：清空仓库→查询→勾选可配货记录"""
        # 货权池弹窗嵌套在"采购货物认领"弹窗之上打开，取最后一个 el-dialog
        dialog = self.page.locator('div.el-dialog').last
        dialog.wait_for(state="visible", timeout=15000)

        # 1. 清空仓库已选值（el-select 用 clear 按钮，不能用 Backspace/fill）
        # 通过"仓库"label 定位所在 form-item 内的 el-select
        warehouse_select = dialog.locator(
            ".el-form-item__label:has-text('仓库')"
        ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]").locator(".el-select").first
        warehouse_select.wait_for(state="visible", timeout=8000)
        clear_el_select(self.page, warehouse_select, desc="货权池-仓库")

        # 2. 点击弹窗内的"搜索"按钮（限定在弹窗范围内，避免点到页面其它搜索按钮）
        logger.info("货权池: 点击'搜索'")
        dialog.locator("button:has-text('搜索')").click()
        self.page.wait_for_timeout(2000)

        # 3. 勾选第一条记录（vxe-table 选择列为 checkbox，表体行用 tr.vxe-body--row 定位可见元素）
        logger.info("货权池: 勾选第一条记录")
        checkbox = dialog.locator("tr.vxe-body--row .vxe-cell--checkbox:visible").first
        checkbox.wait_for(state="visible", timeout=10000)
        checkbox.click()
        self.page.wait_for_timeout(800)
        logger.info("货权池: 第一条记录已选中")

    def confirm_pool(self):
        """步骤7：确定（限定弹窗底部 footer 的确定按钮，避免匹配多个）"""
        dialog = self.page.locator('div.el-dialog').last
        logger.info("货权池: 点击'确定'")
        dialog.locator(".el-dialog__footer button:has-text('确定')").last.click()
        time.sleep(2)

    def fill_details(self):
        """步骤8：配货重量=2，数量=0，是否补单=否"""
        # 可见的 number 输入框：第1个是本次配货重量，第2个是本次配货数量（固定列克隆不可见）
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

        # 是否补单=否（radio value=0）
        logger.info("配货: 是否补单=否")
        self.page.locator(".el-dialog .el-radio:has(input[value='0'])").first.click()
        self.page.wait_for_timeout(300)

    def save(self):
        """步骤9：保存→确定，等待弹窗关闭并返回是否出现成功提示"""
        dialog = self.page.locator('.el-dialog').last

        # 1. 点击保存
        logger.info("保存: 点击'保存'")
        save_btn = dialog.locator(".el-dialog__footer button:has-text('保存')")
        save_btn.click()
        self.page.wait_for_timeout(2000)

        # 2. 点击确定
        logger.info("保存: 点击'确定'")
        confirm_btn = self.page.locator('.el-dialog').last.locator(".el-dialog__footer button:has-text('确定')")
        confirm_btn.click()

        # 3. 立即检测成功提示（提示可能很快消失，需在弹窗关闭前后都检测）
        success = False
        try:
            ok_tip = self.page.locator("[class*='message'], [class*='toast'], [class*='notification'], [class*='tip']").filter(has_text="ok")
            ok_tip.first.wait_for(state="visible", timeout=8000)
            success = True
            logger.info("保存: 成功提示已出现")
        except Exception:
            logger.info("保存: 快速检测未捕获到提示，继续等待弹窗关闭")

        # 4. 等待采购货物认领弹窗关闭
        if not success:
            try:
                dialog.wait_for(state="hidden", timeout=15000)
                logger.info("保存: 弹窗已关闭")
                # 弹窗关闭说明保存成功，再尝试检测一次提示
                try:
                    ok_tip = self.page.locator("[class*='message'], [class*='toast'], [class*='notification'], [class*='tip']").filter(has_text="ok")
                    ok_tip.first.wait_for(state="visible", timeout=3000)
                    success = True
                    logger.info("保存: 成功提示已出现")
                except Exception:
                    # 弹窗关闭即视为保存成功
                    success = True
                    logger.info("保存: 弹窗已关闭，视为保存成功")
            except Exception:
                logger.warning("保存: 弹窗未在15秒内关闭")
        return success

    def execute_purchase_claim(self, contract_code):
        """执行完整的采购货物认领流程（每步报错自动截图），返回保存是否成功"""
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