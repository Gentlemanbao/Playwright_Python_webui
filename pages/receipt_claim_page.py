# -*- coding: utf-8 -*-
"""
Author: 章豹
Date: 2026-10-22
LastEditors: Do not edit
LastEditTime: 2026-10-22

收款认领页面对象
"""
import time
from utils.log_print import get_logger
from utils.save_screenshot import save_screenshot

logger = get_logger()


class ReceiptClaimPage:
    """收款认领页面"""

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

    def select_receipt_claim(self):
        """步骤3：点击收付款 → 选择收款认领"""
        logger.info("下拉: 点击'收付款'按钮")
        self.receive_payment_btn.scroll_into_view_if_needed(timeout=5000)
        self.page.wait_for_timeout(500)
        self.receive_payment_btn.click(force=True, timeout=10000)

        # 等待下拉菜单弹出
        logger.info("下拉: 等待菜单弹出")
        self.page.wait_for_timeout(1500)

        # 找到 popper 并选择"收款认领"
        popper = self.page.locator(".el-popper").last
        try:
            popper.wait_for(state="visible", timeout=8000)
            logger.info("下拉: popper 已可见")
        except Exception:
            logger.warning("下拉: .el-popper 未变为可见")

        menu_item = self.page.get_by_text("收款认领", exact=True).first
        try:
            menu_item.wait_for(state="visible", timeout=5000)
            logger.info("下拉: get_by_text 找到'收款认领'")
        except Exception:
            if popper.is_visible():
                menu_item = popper.get_by_text("收款认领", exact=True).first
                menu_item.wait_for(state="visible", timeout=3000)

        menu_item.click()
        logger.info("下拉: 已选择收款认领，等待弹窗加载...")
        self.page.wait_for_timeout(3000)

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
        # 待收款项选择弹窗是新弹出的，取最后一个弹窗
        dialog = self.page.locator('div.el-dialog').last
        dialog.wait_for(state="visible", timeout=10000)
        logger.info("待收款项: 勾选表头全选复选框")

        # 等待表格渲染完成
        self.page.wait_for_timeout(2000)

        # 点击表头的全选勾选框（用 title="全选/取消" 精确定位，force=True 绕过固定列隐藏克隆）
        header_checkbox = dialog.locator(
            "span.vxe-cell--checkbox[title='全选/取消']"
        ).first
        header_checkbox.wait_for(state="attached", timeout=10000)
        header_checkbox.click(force=True)
        self.page.wait_for_timeout(800)
        logger.info("待收款项: 已勾选全选")

        # 点击确认选择按钮
        logger.info("待收款项: 点击'确认选择'")
        confirm_btn = dialog.locator("button:has-text('确认选择')")
        confirm_btn.wait_for(state="visible", timeout=5000)
        confirm_btn.click()
        self.page.wait_for_timeout(2000)
        logger.info("待收款项: 已点击确认选择")

    def confirm_claim(self):
        """步骤6：数据回显到收款认领弹窗后，点击确定"""
        dialog = self.page.locator('.el-dialog').last
        dialog.wait_for(state="visible", timeout=10000)
        logger.info("收款认领: 点击'确定'")
        confirm_btn = dialog.locator(".el-dialog__footer button:has-text('确定')")
        confirm_btn.wait_for(state="visible", timeout=5000)
        confirm_btn.click()
        self.page.wait_for_timeout(2000)
        logger.info("收款认领: 已点击确定")

        # 确定后会弹出一个 MessageBox 弹窗（el-overlay-message-box），需要点击关闭按钮
        logger.info("收款认领: 关闭结果弹窗")
        self.page.wait_for_timeout(2000)
        try:
            msg_box = self.page.locator('.el-overlay-message-box').last
            msg_box.wait_for(state="visible", timeout=10000)
            # 在 message-box 的按钮区域找"关闭"按钮
            close_btn = msg_box.locator(".el-message-box__btns button:has-text('关闭')")
            close_btn.wait_for(state="visible", timeout=5000)
            close_btn.click()
            self.page.wait_for_timeout(1000)
            logger.info("收款认领: 已关闭结果弹窗")
        except Exception as e:
            logger.warning(f"收款认领: 关闭按钮点击异常: {e}")

    def assert_success(self):
        """步骤7：断言提交成功提示文案 ok"""
        logger.info("断言: 等待成功提示...")
        ok_tip = self.page.locator(
            "[class*='message'], [class*='toast'], [class*='notification'], [class*='tip']"
        ).filter(has_text="ok")
        ok_tip.first.wait_for(state="visible", timeout=120000)
        success = ok_tip.count() > 0
        assert success, "收款认领未检测到成功提示"
        logger.info("断言: 收款认领成功提示已出现")
        save_screenshot(self.page, "收款认领成功")
        return success

    def execute_receipt_claim(self, contract_code):
        """执行完整的收款认领流程（每步报错自动截图）"""
        steps = [
            ("01_navigate", lambda: self.navigate_and_search(contract_code)),
            ("02_switch_tab", lambda: self.switch_to_settlement_tab()),
            ("03_select_claim", lambda: self.select_receipt_claim()),
            ("04_click_pending", lambda: self.click_pending_receipt()),
            ("05_select_all", lambda: self.select_all_items()),
            ("06_confirm", lambda: self.confirm_claim()),
            ("07_assert", lambda: self.assert_success()),
        ]
        result = None
        for step_name, step_fn in steps:
            result = self._execute_step(step_name, step_fn)
        return result
