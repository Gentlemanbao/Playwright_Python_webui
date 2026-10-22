# -*- coding: utf-8 -*-
"""
Author: 章豹
Date: 2026-10-22
LastEditors: Do not edit
LastEditTime: 2026-10-22

销售配货页面对象
"""
import time
from datetime import datetime, timedelta
from utils.log_print import get_logger
from utils.save_screenshot import save_screenshot
from pages.public_operation import select_dropdown_option, fill_date_picker, get_vxe_table_by_header, vxe_fill_cell

logger = get_logger()


class SaleDistributionPage:
    """销售配货页面"""

    def __init__(self, page):
        self.page = page

        # ===== 菜单导航 =====
        self.contract_management_menu = page.locator(".vben-sub-menu:has-text('合同管理')")
        self.contract_bookkeeping_menu = page.locator(".vben-menu-item__content:has-text('合同簿记')")
        self.search_contract_input = page.locator("[placeholder='请输入合约编号']")
        self.search_btn = page.locator("button:has-text('搜索')")

        # ===== 合同详情 Tabs =====
        self.settlement_tab = page.locator(".el-tabs__item").filter(has_text="结")

        # ===== 结算 tab：收发货按钮 → 销售配货 =====
        self.receive_dispatch_btn = page.locator("button").filter(has_text="收发货")

        # ===== 销售配货弹窗 =====
        self.add_data_btn = page.locator("button:has-text('添加数据')")

    def _execute_step(self, step_name, fn):
        """执行单个步骤，报错时自动截图并抛出"""
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

        # 等待合同详情加载
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
        """步骤2：切换到结算tab"""
        logger.info("Tab: 切换到'结算'")
        self.settlement_tab.click()
        time.sleep(2)
        logger.info("Tab: 已切换到结算")

    def select_sale_distribution(self):
        """步骤3：点击收发货 → 选择销售配货"""
        logger.info("下拉: 点击'收发货'按钮")
        # 先滚动到可视区域，再用 force=True 确保点击生效
        self.receive_dispatch_btn.scroll_into_view_if_needed(timeout=5000)
        self.page.wait_for_timeout(500)
        self.receive_dispatch_btn.click(force=True, timeout=10000)

        # 等待下拉菜单弹出：先等 popper 容器出现且可见
        logger.info("下拉: 等待菜单弹出")
        self.page.wait_for_timeout(1500)  # 给动画一点时间

        # 查找所有可见的 popper/下拉菜单
        popper = self.page.locator(".el-popper").last
        try:
            popper.wait_for(state="visible", timeout=8000)
            logger.info("下拉: popper 已可见")
        except Exception:
            logger.warning("下拉: .el-popper 未变为可见，尝试其他方式定位")

        # 用 Playwright 内置文本匹配查找任何可见的"销售配货"元素
        logger.info("下拉: 查找'销售配货'选项")
        menu_item = self.page.get_by_text("销售配货", exact=True).first
        try:
            menu_item.wait_for(state="visible", timeout=5000)
            logger.info("下拉: get_by_text 找到元素")
        except Exception:
            # 兜底：在 popper 内查找
            logger.info("下拉: 尝试在 popper 内查找")
            if popper.is_visible():
                menu_item = popper.get_by_text("销售配货", exact=True).first
                menu_item.wait_for(state="visible", timeout=3000)

        menu_item.click()
        logger.info("下拉: 已选择销售配货，等待弹窗加载...")
        self.page.wait_for_timeout(5000)
        logger.info("下拉: 已选择销售配货，等待弹窗加载...")
        self.page.wait_for_timeout(5000)

    def select_batch(self):
        """步骤4：在销售配货弹窗左侧勾选第一条结算批次"""
        logger.info("批次: 勾选左侧第一条结算批次")
        # 销售配货弹窗左侧的结算批次表格，勾选第一行的checkbox
        dialog = self.page.locator('.el-dialog').last
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
        """步骤6：货权池弹窗 → 展开查询条件 → 选账号类型=在库 → 搜索 → 勾选第一条"""
        dialog = self.page.locator('div.el-dialog').last
        dialog.wait_for(state="visible", timeout=15000)

        # 0. 先点开展开按钮（查询条件默认折叠）
        logger.info("货权池: 点开展开按钮")
        expand_btn = dialog.locator("button.el-button--primary.is-link:has-text('展开 ')")
        if expand_btn.count() > 0 and expand_btn.is_visible():
            expand_btn.click()
            self.page.wait_for_timeout(1000)
            logger.info("货权池: 已点开展开按钮")

        # 1. 账号类型下拉 → 选择"在库"
        account_type_select = dialog.locator(
            ".el-form-item__label:has-text('账号类型')"
        ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]").locator(".el-select").first
        account_type_select.wait_for(state="visible", timeout=8000)
        select_dropdown_option(self.page, account_type_select, "在库", desc="货权池-账号类型")

        # 2. 点击搜索按钮（图标按钮，限定在弹窗内）
        logger.info("货权池: 点击搜索按钮")
        search_icon_btn = dialog.locator("button.el-button:has(.el-icon-search)")
        if search_icon_btn.count() > 0:
            search_icon_btn.first.click()
        else:
            # 兜底：找任意带搜索图标的按钮
            dialog.locator("button:has(.el-icon-search), button:has-text('搜索')").first.click()
        self.page.wait_for_timeout(2000)

        # 3. 勾选第一条记录
        logger.info("货权池: 勾选第一条记录")
        checkbox = dialog.locator("tr.vxe-body--row .vxe-cell--checkbox:visible").first
        checkbox.wait_for(state="visible", timeout=10000)
        checkbox.click()
        self.page.wait_for_timeout(800)
        logger.info("货权池: 第一条记录已选中")

    def confirm_pool(self):
        """步骤7：点击货权池弹窗的确定按钮"""
        dialog = self.page.locator('div.el-dialog').last
        logger.info("货权池: 点击'确定'")
        dialog.locator(".el-dialog__footer button:has-text('确定')").last.click()
        time.sleep(2)

    def fill_details(self):
        """步骤8：填写仓储费截止日、提单截止日、交货方式、配货重量、配货数量"""
        today = datetime.now().strftime("%Y-%m-%d")
        future = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

        # 销售配货弹窗（货权池关闭后，只剩销售配货弹窗）
        dialog = self.page.locator('.el-dialog').last

        # 仓储费截止日 = 今天
        logger.info(f"填写: 仓储费截止日={today}")
        storage_end = dialog.locator(
            ".el-form-item__label:has-text('仓储费截止日')"
        ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]").locator("input").first
        fill_date_picker(self.page, storage_end, today)

        # 提单截止日 = 今天+7天
        logger.info(f"填写: 提单截止日={future}")
        bill_end = dialog.locator(
            ".el-form-item__label:has-text('提单截止日')"
        ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]").locator("input").first
        fill_date_picker(self.page, bill_end, future)
        # 交货方式 = 货转
        logger.info("填写: 交货方式=货转")
        delivery_method = dialog.locator(
            ".el-form-item__label:has-text('交货方式')"
        ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]").locator(".el-select").first
        select_dropdown_option(self.page, delivery_method, "货转", desc="销售配货-交货方式")

        logger.info("填写: 配货重量=2")
        table = get_vxe_table_by_header(self.page, marker_header="账号类型")
        vxe_fill_cell(self.page, table, "配货重量", "2", field_type='spinbutton')

        # 配货数量 = 0
        logger.info("填写: 配货数量=0")
        vxe_fill_cell(self.page, table, "配货数量", "0", field_type='spinbutton')

    def save(self):
        """步骤9：点击保存"""
        dialog = self.page.locator('.el-dialog').last
        logger.info("保存: 点击'保存'")
        save_btn = dialog.locator(".el-dialog__footer button:has-text('保存')")
        save_btn.click()
        self.page.wait_for_timeout(2000)
        time.sleep(2)
        logger.info("保存: 完成")

    def deliver_and_assert(self):
        """步骤9：点击配货出库，断言提示语OK（接口响应可能较慢，等待时间长一些）"""
        logger.info("配货出库: 点击'配货出库'")
        deliver_btn = self.page.locator("button:has-text('配货出库')")
        deliver_btn.wait_for(state="visible", timeout=10000)
        deliver_btn.click()
        self.page.wait_for_timeout(2000)

        # 断言提示语OK（接口响应可能较慢，设置较长超时）
        logger.info("断言: 等待成功提示...")
        ok_tip = self.page.locator(
            "[class*='message'], [class*='toast'], [class*='notification'], [class*='tip']"
        ).filter(has_text="ok")
        ok_tip.first.wait_for(state="visible", timeout=120000)
        success = ok_tip.count() > 0
        assert success, "配货出库未检测到成功提示"
        logger.info("断言: 配货出库成功提示已出现")
        save_screenshot(self.page, "销售配货成功")
        return success

    def execute_sale_distribution(self, contract_code):
        """执行完整的销售配货流程（每步报错自动截图）"""
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
