# -*- coding: utf-8 -*-
"""
Author: 章豹
Date: 2026-10-23

合同结算工作流基类
封装"合同管理→合同簿记→搜索合同→切换到结算tab"的公共入口操作，
以及通用的下拉菜单选择方法。
所有货款票操作页面（采购货物认领、收款认领、销售配货、付款申请等）继承此类。
"""
import time
from utils.log_print import get_logger
from utils.save_screenshot import save_screenshot

logger = get_logger()


class BaseSettlementPage:
    """合同结算工作流基类"""

    def __init__(self, page):
        self.page = page

        # ===== 菜单导航（所有页面共用） =====
        self.contract_management_menu = page.locator(".vben-sub-menu:has-text('合同管理')")
        self.contract_bookkeeping_menu = page.locator(".vben-menu-item__content:has-text('合同簿记')")
        self.search_contract_input = page.locator("[placeholder='请输入合约编号']")
        self.search_btn = page.locator("button:has-text('搜索')")

        # ===== 合同详情 Tabs =====
        self.settlement_tab = page.locator(".el-tabs__item").filter(has_text="结")

    # ---- 公共步骤方法 ----

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

    def click_dropdown_button(self, button_locator):
        """点击下拉按钮（收付款/收发货），等待popper弹出"""
        logger.info("下拉: 点击按钮")
        button_locator.scroll_into_view_if_needed(timeout=5000)
        self.page.wait_for_timeout(500)
        button_locator.click(force=True, timeout=10000)

        self.page.wait_for_timeout(1500)
        popper = self.page.locator(".el-popper").last
        try:
            popper.wait_for(state="visible", timeout=8000)
            logger.info("下拉: popper 已可见")
        except Exception:
            logger.warning("下拉: .el-popper 未变为可见")
        return popper

    def select_dropdown_item(self, item_text):
        """在下拉菜单中选择指定文本的选项"""
        logger.info(f"下拉: 选择'{item_text}'")
        menu_item = self.page.get_by_text(item_text, exact=True).first
        try:
            menu_item.wait_for(state="visible", timeout=5000)
        except Exception:
            popper = self.page.locator(".el-popper").last
            if popper.is_visible():
                menu_item = popper.get_by_text(item_text, exact=True).first
                menu_item.wait_for(state="visible", timeout=3000)
        menu_item.click()
        logger.info(f"下拉: 已选择'{item_text}'，等待弹窗加载...")
        self.page.wait_for_timeout(3000)

    def click_dialog_confirm(self, dialog=None):
        """在弹窗底部点击'确定'按钮"""
        if dialog is None:
            dialog = self.page.locator('.el-dialog').last
        confirm_btn = dialog.locator(".el-dialog__footer button:has-text('确定')")
        confirm_btn.wait_for(state="visible", timeout=5000)
        confirm_btn.click()
        self.page.wait_for_timeout(2000)
        logger.info("弹窗: 已点击确定")

    def assert_success(self, desc="操作"):
        """断言提交成功提示文案 ok"""
        logger.info(f"断言: 等待'{desc}'成功提示...")
        ok_tip = self.page.locator(
            "[class*='message'], [class*='toast'], [class*='notification'], [class*='tip']"
        ).filter(has_text="ok")
        ok_tip.first.wait_for(state="visible", timeout=120000)
        success = ok_tip.count() > 0
        assert success, f"{desc}未检测到成功提示"
        logger.info(f"断言: '{desc}'成功提示已出现")
        save_screenshot(self.page, f"{desc}成功")
        return success

    def close_message_box(self):
        """关闭 MessageBox 弹窗（el-overlay-message-box），点击关闭按钮"""
        logger.info("弹窗: 关闭 MessageBox")
        self.page.wait_for_timeout(2000)
        try:
            msg_box = self.page.locator('.el-overlay-message-box').last
            msg_box.wait_for(state="visible", timeout=10000)
            close_btn = msg_box.locator(".el-message-box__btns button:has-text('关闭')")
            close_btn.wait_for(state="visible", timeout=5000)
            close_btn.click()
            self.page.wait_for_timeout(1000)
            logger.info("弹窗: MessageBox 已关闭")
        except Exception as e:
            logger.warning(f"弹窗: MessageBox 关闭异常: {e}")
