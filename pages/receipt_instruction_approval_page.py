# -*- coding: utf-8 -*-
"""
Author: 章豹
Date: 2026-10-26

收票指令审批页面对象
覆盖：财务运营→发票指令执行→收票tab→搜索合同→票务专员审批→断言已完成
"""
import time
from utils.log_print import get_logger
from utils.save_screenshot import save_screenshot

logger = get_logger()


class ReceiptInstructionApprovalPage:
    """收票指令审批页面"""

    def __init__(self, page):
        self.page = page

        # ===== 菜单导航 =====
        self.finance_ops_menu = page.locator(".vben-sub-menu:has-text('财务运营')")
        self.invoice_instruction_menu = page.locator(".vben-menu-item__content:has-text('发票指令执行')")

        # ===== 收票 tab =====
        self.receipt_pane = page.locator("#pane-ins-invoice-receive")

        # ===== 搜索区域（限定在收票面板内） =====
        self.contract_code_input = self.receipt_pane.locator("[name='logicContractCode']")
        self.search_btn = self.receipt_pane.locator("button").filter(has_text="搜索")

    def _execute_step(self, step_name, fn):
        """执行单个步骤，报错时自动截图并抛出"""
        try:
            return fn()
        except Exception as e:
            save_screenshot(self.page, f"失败_{step_name}")
            logger.error(f"❌ 步骤 [{step_name}] 执行失败: {e}")
            raise RuntimeError(f"步骤 [{step_name}] 失败: {e}") from e

    def navigate_and_search(self, contract_code):
        """导航到财务运营→发票指令执行→收票tab→搜索合同号"""
        logger.info("导航: 点击'财务运营'")
        self.finance_ops_menu.click()
        time.sleep(0.5)

        logger.info("导航: 点击'发票指令执行'")
        self.invoice_instruction_menu.click()
        time.sleep(2)

        self._do_search(contract_code)

    def _do_search(self, contract_code):
        """在收票tab中输入合同号并搜索"""
        code = str(contract_code)
        logger.info(f"搜索: 填入合同号 {code}")

        # el-select 下拉框：点击展开，输入合同号
        self.contract_code_input.click()
        self.page.wait_for_timeout(500)
        self.contract_code_input.fill(code)

        # 等待下拉框加载出匹配的合同号（网络慢时可能需要更长时间）
        self.page.wait_for_timeout(3000)

        # 按 ArrowDown + Enter 选择下拉列表中匹配的合同号
        self.contract_code_input.press("ArrowDown")
        self.page.wait_for_timeout(500)
        self.contract_code_input.press("Enter")
        self.page.wait_for_timeout(1500)
        logger.info(f"搜索: 已选择合同号 {code}")

        # 点击搜索
        self.search_btn.first.click()
        self.page.wait_for_timeout(3000)
        logger.info("搜索: 已搜索")

    def _click_action_button(self, button_text):
        """点击列表第一条数据操作列的指定按钮/链接"""
        logger.info(f"操作: 点击'{button_text}'")
        self.page.wait_for_timeout(3000)
        btn = self.page.locator(".vxe-body--column").locator("a, button").filter(has_text=button_text).first
        btn.wait_for(state="attached", timeout=15000)
        btn.scroll_into_view_if_needed(timeout=5000)
        self.page.wait_for_timeout(500)
        btn.click(force=True, timeout=10000)
        self.page.wait_for_timeout(2000)
        logger.info(f"操作: 已点击'{button_text}'")

    def _approve(self, opinion_text, button_text):
        """
        通用审批步骤：
        1. 点击操作列的审批按钮
        2. 在审批弹窗中输入审核意见
        3. 点击审核通过
        4. 断言"操作成功"
        5. 重新搜索合同号
        """
        # 1. 点击审批按钮
        self._click_action_button(button_text)

        # 2. 输入审核意见（通过 label 定位）
        logger.info(f"审批: 输入审核意见'{opinion_text}'")
        dialog = self.page.locator('.el-dialog').last
        try:
            dialog.wait_for(state="visible", timeout=5000)
        except Exception:
            dialog = self.page.locator('.el-overlay-message-box').last
            dialog.wait_for(state="visible", timeout=5000)

        opinion_form_item = dialog.locator(".el-form-item__label:has-text('审核意见')").locator(
            "xpath=ancestor::div[contains(@class,'el-form-item')]"
        )
        opinion_input = opinion_form_item.locator("textarea")
        opinion_input.wait_for(state="attached", timeout=5000)
        opinion_input.fill(opinion_text)
        self.page.wait_for_timeout(500)
        logger.info(f"审批: 已输入意见'{opinion_text}'")

        # 3. 点击审核通过
        logger.info("审批: 点击'审核通过'")
        approve_btn = dialog.locator("button:has-text('审核通过')")
        approve_btn.wait_for(state="visible", timeout=5000)
        approve_btn.click()
        self.page.wait_for_timeout(2000)
        logger.info("审批: 已点击审核通过")

        # 4. 断言"操作成功"
        self._assert_operation_success()

        # 5. 重新搜索合同号（页面刷新后搜索条件被清空）
        self._do_search(self._contract_code)

    def _assert_operation_success(self):
        """断言操作成功提示"""
        logger.info("断言: 等待'操作成功'提示...")
        success_tip = self.page.locator(
            "[class*='message'], [class*='toast'], [class*='notification'], [class*='tip']"
        ).filter(has_text="操作成功")
        success_tip.first.wait_for(state="visible", timeout=120000)
        logger.info("断言: '操作成功'提示已出现")

    def _assert_status_completed(self):
        """断言第一条数据的状态为'已完成'"""
        logger.info("断言: 检查状态是否为'已完成'")
        self.page.wait_for_timeout(2000)
        completed = self.page.locator(".vxe-body--column").filter(has_text="已完成").first
        completed.wait_for(state="attached", timeout=15000)
        assert completed.count() > 0, "状态未显示'已完成'"
        logger.info("断言: 状态已显示'已完成'")
        save_screenshot(self.page, "收票指令审批完成")

    def execute_full_approval(self, contract_code):
        """执行完整的收票指令审批流程"""
        self._contract_code = contract_code

        steps = [
            ("01_navigate_search", lambda: self.navigate_and_search(contract_code)),
            ("02_approve_ticket", lambda: self._approve("票务专员审批通过", "票务专员审批")),
            ("03_assert_completed", lambda: self._assert_status_completed()),
        ]
        for step_name, step_fn in steps:
            self._execute_step(step_name, step_fn)
        return True
