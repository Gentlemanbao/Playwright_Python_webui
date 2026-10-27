# -*- coding: utf-8 -*-
"""
Author: 章豹
Date: 2026-10-27

开票指令审批页面对象
覆盖：财务运营→发票指令执行→开票tab→搜索合同→财务初审→匹配库存→断言成功
"""
import time
import re
from utils.log_print import get_logger
from utils.save_screenshot import save_screenshot

logger = get_logger()


class MakeInvoiceApprovalPage:
    """开票指令审批页面"""

    def __init__(self, page):
        self.page = page

        # ===== 菜单导航 =====
        self.finance_ops_menu = page.locator(".vben-sub-menu:has-text('财务运营')")
        self.invoice_instruction_menu = page.locator(".vben-menu-item__content:has-text('发票指令执行')")

        # ===== 开票 tab =====
        self.make_invoice_tab = page.locator("#tab-ins-invoice-makeout")
        self.make_invoice_pane = page.locator("#pane-ins-invoice-makeout")

        # ===== 搜索区域（限定在开票面板内） =====
        self.contract_code_input = self.make_invoice_pane.locator("[name='logicContractCode']")
        self.search_btn = self.make_invoice_pane.locator("button").filter(has_text="搜索")

    def _execute_step(self, step_name, fn):
        """执行单个步骤，报错时自动截图并抛出"""
        try:
            return fn()
        except Exception as e:
            save_screenshot(self.page, f"失败_{step_name}")
            logger.error(f"❌ 步骤 [{step_name}] 执行失败: {e}")
            raise RuntimeError(f"步骤 [{step_name}] 失败: {e}") from e

    def navigate_and_search(self, contract_code):
        """导航到财务运营→发票指令执行→切换到开票tab→搜索合同号"""
        logger.info("导航: 点击'财务运营'")
        self.finance_ops_menu.click()
        time.sleep(0.5)

        logger.info("导航: 点击'发票指令执行'")
        self.invoice_instruction_menu.click()
        time.sleep(2)

        # 切换到开票 tab
        logger.info("Tab: 切换到'开票'")
        self.make_invoice_tab.click()
        time.sleep(2)

        # 搜索合同号
        code = str(contract_code)
        logger.info(f"搜索: 填入合同号 {code}")
        self.contract_code_input.click()
        self.page.wait_for_timeout(500)
        self.contract_code_input.fill(code)
        self.page.wait_for_timeout(1000)

        # 按 ArrowDown + Enter 选择合同号
        self.contract_code_input.press("ArrowDown")
        self.page.wait_for_timeout(800)
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

    def _assert_operation_success(self):
        """断言操作成功提示"""
        logger.info("断言: 等待'操作成功'提示...")
        success_tip = self.page.locator(
            "[class*='message'], [class*='toast'], [class*='notification'], [class*='tip']"
        ).filter(has_text="操作成功")
        success_tip.first.wait_for(state="visible", timeout=120000)
        logger.info("断言: '操作成功'提示已出现")

    def _do_search(self, contract_code):
        """搜索合同号（页面刷新后重新搜索）"""
        code = str(contract_code)
        logger.info(f"搜索: 填入合同号 {code}")
        self.contract_code_input.click()
        self.page.wait_for_timeout(500)
        self.contract_code_input.fill(code)
        self.page.wait_for_timeout(1000)
        self.contract_code_input.press("ArrowDown")
        self.page.wait_for_timeout(800)
        self.contract_code_input.press("Enter")
        self.page.wait_for_timeout(1500)
        self.search_btn.first.click()
        self.page.wait_for_timeout(3000)
        logger.info("搜索: 已搜索")

    def _approve(self, opinion_text, button_text):
        """
        通用审批步骤：
        1. 点击操作列的审批按钮
        2. 输入审核意见
        3. 点击审核通过
        4. 断言操作成功
        5. 重新搜索
        """
        self._click_action_button(button_text)

        # 输入审核意见
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

        # 点击审核通过
        logger.info("审批: 点击'审核通过'")
        approve_btn = dialog.locator("button:has-text('审核通过')")
        approve_btn.wait_for(state="visible", timeout=5000)
        approve_btn.click()
        self.page.wait_for_timeout(2000)
        logger.info("审批: 已点击审核通过")

        # 断言操作成功
        self._assert_operation_success()

        # 重新搜索（审批后列表状态变了，必须刷新才能看到"匹配库存"按钮）
        self._do_search(self._contract_code)

    def _find_dialog_idx_by_text(self, *keywords):
        """JS 扫描找包含所有关键字的弹窗 index（避免 .last 拿错）"""
        idx = self.page.evaluate("""(keywords) => {
            const dlgs = document.querySelectorAll('.el-dialog');
            for (let i = 0; i < dlgs.length; i++) {
                const text = dlgs[i].textContent || '';
                if (keywords.every(k => text.includes(k))) return i;
            }
            return -1;
        }""", list(keywords))
        logger.info(f"弹窗扫描: keywords={keywords}, 找到 nth={idx}, 总弹窗数={self.page.locator('.el-dialog').count()}")
        return idx

    def _click_confirm_match_button(self):
        """在匹配库存弹窗里点击"确认匹配"按钮"""
        idx = self._find_dialog_idx_by_text("确认匹配", "发票池")
        if idx == -1:
            raise RuntimeError("未找到包含'确认匹配'+'发票池'的弹窗")
        dialog = self.page.locator(".el-dialog").nth(idx)
        dialog.wait_for(state="visible", timeout=10000)

        confirm_match_btn = dialog.locator("button").filter(has_text=re.compile(r"确认匹配")).first
        confirm_match_btn.wait_for(state="attached", timeout=10000)
        logger.info("匹配库存: 点击'确认匹配'按钮")
        confirm_match_btn.click(force=True, timeout=10000)
        self.page.wait_for_timeout(3000)
        logger.info("匹配库存: 已点击确认匹配")

    def _click_final_confirm(self):
        """匹配库存后点最终确认（可能是 dialog 里的"确认"也可能是 message-box 里的"确定"）"""
        logger.info("匹配库存: 点击最终确认按钮")
        # 先查 message-box（二次弹窗）
        msg_box = self.page.locator(".el-overlay-message-box").last
        if msg_box.count() and msg_box.first.is_visible():
            btn = msg_box.locator("button").filter(has_text=re.compile(r"确定|确认")).first
            btn.wait_for(state="visible", timeout=5000)
            btn.click(force=True, timeout=5000)
        else:
            # 兜底：找包含"确认"按钮的 dialog
            idx = self._find_dialog_idx_by_text("确认匹配", "发票池")
            if idx >= 0:
                dialog = self.page.locator(".el-dialog").nth(idx)
            else:
                dialog = self.page.locator(".el-dialog").last
            confirm_btn = dialog.locator("button").filter(has_text=re.compile(r"^\s*确认\s*$")).last
            confirm_btn.wait_for(state="attached", timeout=10000)
            confirm_btn.click(force=True, timeout=10000)
        self.page.wait_for_timeout(2000)
        logger.info("匹配库存: 已点击最终确认")
        self._assert_operation_success()

    def execute_full_approval(self, contract_code):
        """执行完整的开票指令审批流程"""
        self._contract_code = contract_code

        self.navigate_and_search(contract_code)
        self._approve("财务初审通过", "财务初审")

        # 点击"匹配库存"打开弹窗
        self._click_action_button("匹配库存")

        # 等前端自动匹配完成
        self.page.wait_for_timeout(5000)

        # 点击"确认匹配"
        self._click_confirm_match_button()

        # 点击"确认"
        self._click_final_confirm()

        return True
