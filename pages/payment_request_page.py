# -*- coding: utf-8 -*-
"""
Author: 章豹
Date: 2026-10-22
LastEditors: Do not edit
LastEditTime: 2026-10-22

付款申请页面对象
"""
import time
from datetime import datetime
from utils.log_print import get_logger
from utils.save_screenshot import save_screenshot
from pages.public_operation import select_dropdown_option, fill_date_picker, get_vxe_table_by_header, vxe_fill_cell

logger = get_logger()


class PaymentRequestPage:
    """付款申请页面"""

    def __init__(self, page):
        self.page = page

        # ===== 菜单导航 =====
        self.contract_management_menu = page.locator(".vben-sub-menu:has-text('合同管理')")
        self.contract_bookkeeping_menu = page.locator(".vben-menu-item__content:has-text('合同簿记')")
        self.search_contract_input = page.locator("[placeholder='请输入合约编号']")
        self.search_btn = page.locator("button:has-text('搜索')")

        # ===== 合同详情 Tabs =====
        self.settlement_tab = page.locator(".el-tabs__item").filter(has_text="结")

        # ===== 结算 tab：收付款按钮 =====
        self.receive_payment_btn = page.locator("button").filter(has_text=" 收付款 ")

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

    def select_payment_request(self):
        """步骤3：点击收付款 → 选择付款申请"""
        logger.info("下拉: 点击'收付款'按钮")
        self.receive_payment_btn.scroll_into_view_if_needed(timeout=5000)
        self.page.wait_for_timeout(500)
        self.receive_payment_btn.click(force=True, timeout=10000)

        # 等待下拉菜单弹出
        logger.info("下拉: 等待菜单弹出")
        self.page.wait_for_timeout(1500)

        popper = self.page.locator(".el-popper").last
        try:
            popper.wait_for(state="visible", timeout=8000)
            logger.info("下拉: popper 已可见")
        except Exception:
            logger.warning("下拉: .el-popper 未变为可见")

        menu_item = self.page.get_by_text("付款申请", exact=True).first
        try:
            menu_item.wait_for(state="visible", timeout=5000)
            logger.info("下拉: get_by_text 找到'付款申请'")
        except Exception:
            if popper.is_visible():
                menu_item = popper.get_by_text("付款申请", exact=True).first
                menu_item.wait_for(state="visible", timeout=3000)

        menu_item.click()
        logger.info("下拉: 已选择付款申请，等待弹窗加载...")
        self.page.wait_for_timeout(3000)

    def fill_form(self):
        """步骤4：在付款申请弹窗中填写表单"""
        dialog = self.page.locator('.el-dialog').last
        dialog.wait_for(state="visible", timeout=10000)
        logger.info("付款申请: 填写表单")

        # 1. 客户银行账号 - 选择第一个可用选项
        logger.info("填写: 客户银行账号")
        bank_account = dialog.locator(
            ".el-form-item__label:has-text('客户银行账号')"
        ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]").locator(".el-select").first
        bank_account.wait_for(state="visible", timeout=8000)
        select_dropdown_option(self.page, bank_account, "上海市-上海市,中国光大银行股份有限公司上海分行-35500188069094023", desc="付款申请-客户银行账号")

        # 2. 付款期限 = 当天日期
        today = datetime.now().strftime("%Y-%m-%d")
        logger.info(f"填写: 付款期限={today}")
        pay_deadline = dialog.locator(
            ".el-form-item__label:has-text('付款期限')"
        ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]").locator("input").first
        fill_date_picker(self.page, pay_deadline, today)

        # 3. 付款方式 = 前TT
        logger.info("填写: 付款方式=前TT")
        pay_method = dialog.locator(
            ".el-form-item__label:has-text('付款方式')"
        ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]").locator(".el-select").first
        select_dropdown_option(self.page, pay_method, "前TT", desc="付款申请-付款方式")

        # 4. 账户类型 = 现金账户
        logger.info("填写: 账户类型=现金账户")
        account_type = dialog.locator(
            ".el-form-item__label:has-text('账户类型')"
        ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]").locator(".el-select").first
        select_dropdown_option(self.page, account_type, "现金账户", desc="付款申请-账户类型")

        # 5. 备注 = 测试备注
        logger.info("填写: 备注=测试备注")
        remark = dialog.locator(
            ".el-form-item__label:has-text('备注')"
        ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]").locator("textarea, input").first
        remark.wait_for(state="visible", timeout=5000)
        remark.fill("测试备注")
        self.page.wait_for_timeout(500)

        logger.info("付款申请: 表单填写完成")

    def click_pending_payment(self):
        """步骤5：点击待付款项按钮，在弹出的弹窗中选择第一条数据并确认"""
        dialog = self.page.locator('.el-dialog').last
        logger.info("付款申请: 点击'待付款项'")
        pending_btn = dialog.locator("button:has-text(' 待付款项 ')")
        pending_btn.wait_for(state="visible", timeout=5000)
        pending_btn.click()
        self.page.wait_for_timeout(2000)

        # 待付款项选择弹窗，取最后一个弹窗
        select_dialog = self.page.locator('div.el-dialog').last
        select_dialog.wait_for(state="visible", timeout=10000)
        logger.info("待付款项: 选择第一条数据")

        # 勾选第一条记录的 checkbox
        checkbox = select_dialog.locator("tr.vxe-body--row .vxe-cell--checkbox:visible").first
        checkbox.wait_for(state="visible", timeout=10000)
        checkbox.click()
        self.page.wait_for_timeout(800)
        logger.info("待付款项: 已勾选第一条")

        # 点击确认选择
        logger.info("待付款项: 点击'确认选择'")
        confirm_btn = select_dialog.locator("button:has-text('确认选择')")
        confirm_btn.wait_for(state="visible", timeout=5000)
        confirm_btn.click()
        self.page.wait_for_timeout(2000)
        logger.info("待付款项: 已点击确认选择")

    def fill_weight_and_confirm(self):
        """步骤6：数据回显后，向右滚动列表，在申请重量输入框输入2，点击确定"""
        dialog = self.page.locator('.el-dialog').last
        dialog.wait_for(state="visible", timeout=10000)
        logger.info("付款申请: 向右滚动列表")

        # 横向滚动表格到右侧，使申请重量列可见
        self.page.evaluate("document.querySelector('.vxe-table--body-wrapper') && (document.querySelector('.vxe-table--body-wrapper').scrollLeft = 6400)")
        self.page.wait_for_timeout(1000)

        # 在 vxe-table 中找到可编辑的数字输入框（申请重量），取第一个
        logger.info("填写: 申请重量=2")
        editable_input = dialog.locator(".vxe-table .el-input-number .el-input__inner").first
        editable_input.wait_for(state="visible", timeout=5000)
        editable_input.click()
        editable_input.fill("")
        editable_input.fill("2")
        self.page.wait_for_timeout(500)
        logger.info("付款申请: 已填写申请重量")

        # 点击确定
        logger.info("付款申请: 点击'确定'")
        confirm_btn = dialog.locator(".el-dialog__footer button:has-text('确定')")
        confirm_btn.wait_for(state="visible", timeout=5000)
        confirm_btn.click()
        self.page.wait_for_timeout(2000)
        logger.info("付款申请: 已点击确定")

    def assert_success(self):
        """步骤7：断言提交成功提示文案 ok"""
        logger.info("断言: 等待成功提示...")
        ok_tip = self.page.locator(
            "[class*='message'], [class*='toast'], [class*='notification'], [class*='tip']"
        ).filter(has_text="ok")
        ok_tip.first.wait_for(state="visible", timeout=120000)
        success = ok_tip.count() > 0
        assert success, "付款申请未检测到成功提示"
        logger.info("断言: 付款申请成功提示已出现")
        save_screenshot(self.page, "付款申请成功")
        return success

    def execute_payment_request(self, contract_code):
        """执行完整的付款申请流程（每步报错自动截图）"""
        steps = [
            ("01_navigate", lambda: self.navigate_and_search(contract_code)),
            ("02_switch_tab", lambda: self.switch_to_settlement_tab()),
            ("03_select_payment", lambda: self.select_payment_request()),
            ("04_fill_form", lambda: self.fill_form()),
            ("05_pending_payment", lambda: self.click_pending_payment()),
            ("06_fill_weight_confirm", lambda: self.fill_weight_and_confirm()),
            ("07_assert", lambda: self.assert_success()),
        ]
        result = None
        for step_name, step_fn in steps:
            result = self._execute_step(step_name, step_fn)
        return result
