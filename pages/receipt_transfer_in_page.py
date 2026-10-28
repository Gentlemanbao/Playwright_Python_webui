# -*- coding: utf-8 -*-
"""
Author: 章豹
Date: 2026-10-27

仓单转入页面对象
覆盖：货权运营→货权指令执行→仓单转入tab→新增→填写明细→确定→断言→提取指令编号
"""
import time
import random
from datetime import datetime
from utils.log_print import get_logger
from utils.save_screenshot import save_screenshot
from pages.public_operation import fill_date_picker, select_dropdown_option

logger = get_logger()


class ReceiptTransferInPage:
    """仓单转入页面"""

    def __init__(self, page):
        self.page = page

        # ===== 菜单导航 =====
        self.cargo_ops_menu = page.locator(".vben-sub-menu:has-text('货权运营')")
        self.cargo_instruction_menu = page.locator(".vben-menu-item__content:has-text('货权指令执行')")

        # ===== 仓单转入 tab =====
        self.transfer_in_tab = page.locator("#tab-ins-receipt-transfer-in")
        self.transfer_in_pane = page.locator("#pane-ins-receipt-transfer-in")

        # ===== 列表页操作 =====
        self.add_btn = self.transfer_in_pane.locator("button").filter(has_text="新增")

    def _execute_step(self, step_name, fn):
        """执行单个步骤，报错时自动截图并抛出"""
        try:
            return fn()
        except Exception as e:
            save_screenshot(self.page, f"失败_{step_name}")
            logger.error(f"❌ 步骤 [{step_name}] 执行失败: {e}")
            raise RuntimeError(f"步骤 [{step_name}] 失败: {e}") from e

    def _find_dialog_idx_by_text(self, *keywords):
        """JS 扫描找包含所有关键字的弹窗 index"""
        idx = self.page.evaluate("""(keywords) => {
            const dlgs = document.querySelectorAll('.el-dialog');
            for (let i = 0; i < dlgs.length; i++) {
                const text = dlgs[i].textContent || '';
                if (keywords.every(k => text.includes(k))) return i;
            }
            return -1;
        }""", list(keywords))
        logger.info(f"弹窗扫描: keywords={keywords}, 找到 nth={idx}")
        return idx

    def navigate_and_open_add(self):
        """导航到货权运营→货权指令执行→切换到仓单转入tab→点击新增"""
        logger.info("导航: 点击'货权运营'")
        self.cargo_ops_menu.click()
        time.sleep(0.5)

        logger.info("导航: 点击'货权指令执行'")
        self.cargo_instruction_menu.click()
        time.sleep(2)

        logger.info("Tab: 切换到'仓单转入'")
        self.transfer_in_tab.click()
        time.sleep(2)

        # 点击新增
        logger.info("操作: 点击'新增'")
        self.add_btn.click()
        time.sleep(2)
        logger.info("操作: 已点击新增，弹窗已打开")

    def click_add_detail(self):
        """在第一层弹窗中点击'新增'按钮，打开第二层明细弹窗"""
        idx = self._find_dialog_idx_by_text("指令编号", "指令类型")
        if idx == -1:
            raise RuntimeError("未找到仓单转入新增弹窗")

        dialog = self.page.locator(".el-dialog").nth(idx)
        add_detail_btn = dialog.locator("button").filter(has_text="新增").first
        add_detail_btn.wait_for(state="attached", timeout=10000)
        self.page.wait_for_timeout(500)
        add_detail_btn.click(force=True, timeout=10000)
        self.page.wait_for_timeout(2000)
        logger.info("操作: 已点击明细新增按钮，明细弹窗已打开")

    def fill_detail_form(self):
        """在第二层明细弹窗中填写所有字段"""
        idx = self._find_dialog_idx_by_text("入库日期", "对方主体", "仓单类型")
        if idx == -1:
            raise RuntimeError("未找到仓单转入明细弹窗")

        dialog = self.page.locator(".el-dialog").nth(idx)
        logger.info("明细: 开始填写表单")

        # 1. 入库日期 - 当前日期 2026-10-27
        date_item = dialog.locator(".el-form-item__label:has-text('入库日期')").locator(
            "xpath=ancestor::div[contains(@class,'el-form-item')]"
        )
        date_input = date_item.locator("input[role='combobox']")
        today_str = datetime.now().strftime("%Y-%m-%d")
        fill_date_picker(self.page, date_input, today_str)
        self.page.wait_for_timeout(500)
        logger.info("明细: 已填入库日期")

        # 2. 对方主体 - 北大方正物产集团有限公司
        counterparty_item = dialog.locator(".el-form-item__label:has-text('对方主体')").locator(
            "xpath=ancestor::div[contains(@class,'el-form-item')]"
        )
        counterparty_select = counterparty_item.locator(".el-select").first
        select_dropdown_option(self.page, counterparty_select, "北大方正物产集团有限公司")
        self.page.wait_for_timeout(500)
        logger.info("明细: 已选择对方主体")

        # 3. 品种 - 硅铁
        variety_item = dialog.locator(".el-form-item__label:has-text('品种')").locator(
            "xpath=ancestor::div[contains(@class,'el-form-item')]"
        )
        variety_select = variety_item.locator(".el-select").first
        select_dropdown_option(self.page, variety_select, "硅铁")
        self.page.wait_for_timeout(500)
        logger.info("明细: 已选择品种")

        # 4. 品名 - 硅铁
        product_item = dialog.locator(".el-form-item__label:has-text('品名')").locator(
            "xpath=ancestor::div[contains(@class,'el-form-item')]"
        )
        product_select = product_item.locator(".el-select").first
        select_dropdown_option(self.page, product_select, "硅铁")
        self.page.wait_for_timeout(500)
        logger.info("明细: 已选择品名")

        # 5. 品牌 - 选第一个（点击展开后 ArrowDown+Enter）
        brand_item = dialog.locator(".el-form-item__label:has-text('品牌')").locator(
            "xpath=ancestor::div[contains(@class,'el-form-item')]"
        )
        brand_select = brand_item.locator(".el-select").first
        brand_select.click()
        self.page.wait_for_timeout(1000)
        brand_select.press("ArrowDown")
        self.page.wait_for_timeout(500)
        brand_select.press("Enter")
        self.page.wait_for_timeout(500)
        logger.info("明细: 已选择品牌(第一个)")

        # 6. 规格 - 选第一个（点击展开后 ArrowDown+Enter）
        spec_item = dialog.locator(".el-form-item__label:has-text('规格')").locator(
            "xpath=ancestor::div[contains(@class,'el-form-item')]"
        )
        spec_select = spec_item.locator(".el-select").first
        spec_select.click()
        self.page.wait_for_timeout(1000)
        spec_select.press("ArrowDown")
        self.page.wait_for_timeout(500)
        spec_select.press("Enter")
        self.page.wait_for_timeout(500)
        logger.info("明细: 已选择规格(第一个)")

        # 7. 仓单类型 - 仓库仓单
        type_item = dialog.locator(".el-form-item__label:has-text('仓单类型')").locator(
            "xpath=ancestor::div[contains(@class,'el-form-item')]"
        )
        type_select = type_item.locator(".el-select").first
        type_select.click()
        self.page.wait_for_timeout(500)
        warehouse_option = self.page.locator(".el-select-dropdown__item").filter(has_text="仓库仓单").first
        warehouse_option.wait_for(state="attached", timeout=5000)
        warehouse_option.click(force=True)
        self.page.wait_for_timeout(1000)
        logger.info("明细: 已选择仓单类型")

        # 8. 仓库/港口码头 - 简化处理：直接选下拉第一个（远程搜索太复杂，暂不指定具体值）
        wh_item = dialog.locator(".el-form-item__label:has-text('仓库/港口码头')").locator(
            "xpath=ancestor::div[contains(@class,'el-form-item')]"
        )
        wh_select = wh_item.locator(".el-select").first
        wh_select.click(timeout=5000)
        self.page.wait_for_timeout(1500)  # 等面板渲染 + 远程 API 返回
        self.page.keyboard.press("ArrowDown")
        self.page.wait_for_timeout(300)
        self.page.keyboard.press("Enter")
        self.page.wait_for_timeout(500)
        logger.info("明细: 已选择仓库/港口码头(第一个)")

        # 9. 重量 - 100（用 .last 排除前面的"单位重量"disabled 输入框）
        weight_item = dialog.locator(".el-form-item__label:has-text('重量')").locator(
            "xpath=ancestor::div[contains(@class,'el-form-item')]"
        )
        weight_input = weight_item.locator("input[role='spinbutton']").last
        weight_input.click()
        weight_input.fill("100")
        self.page.wait_for_timeout(500)
        logger.info("明细: 已输入重量")

        # 10. 数量 - 100
        qty_item = dialog.locator(".el-form-item__label:has-text('数量')").locator(
            "xpath=ancestor::div[contains(@class,'el-form-item')]"
        )
        qty_input = qty_item.locator("input[role='spinbutton']").first
        qty_input.click()
        qty_input.fill("100")
        self.page.wait_for_timeout(500)
        logger.info("明细: 已输入数量")

        # 11. 产地 - 测试产地
        origin_item = dialog.locator(".el-form-item__label:has-text('产地')").locator(
            "xpath=ancestor::div[contains(@class,'el-form-item')]"
        )
        origin_input = origin_item.locator("input").first
        origin_input.click()
        origin_input.fill("测试产地")
        self.page.wait_for_timeout(500)
        logger.info("明细: 已输入产地")

        # 12. 批号/捆包号 - 6位随机数字
        batch_item = dialog.locator(".el-form-item__label:has-text('批号/捆包号')").locator(
            "xpath=ancestor::div[contains(@class,'el-form-item')]"
        )
        batch_input = batch_item.locator("input").first
        batch_num = str(random.randint(100000, 999999))
        batch_input.click()
        batch_input.fill(batch_num)
        self.page.wait_for_timeout(500)
        logger.info(f"明细: 已输入批号/捆包号 {batch_num}")

    def click_detail_confirm(self):
        """在第二层明细弹窗中点击确定"""
        idx = self._find_dialog_idx_by_text("入库日期", "对方主体", "仓单类型")
        if idx == -1:
            raise RuntimeError("未找到仓单转入明细弹窗")
        dialog = self.page.locator(".el-dialog").nth(idx)
        confirm_btn = dialog.locator("button").filter(has_text="确定").first
        confirm_btn.wait_for(state="attached", timeout=10000)
        self.page.wait_for_timeout(500)
        confirm_btn.click(force=True, timeout=10000)
        self.page.wait_for_timeout(2000)
        logger.info("明细: 已点击确定")

    def click_main_confirm(self):
        """在第一层弹窗中点击确定"""
        idx = self._find_dialog_idx_by_text("指令编号", "指令类型")
        if idx == -1:
            raise RuntimeError("未找到仓单转入新增弹窗")
        dialog = self.page.locator(".el-dialog").nth(idx)
        confirm_btn = dialog.locator("button").filter(has_text="确定").first
        confirm_btn.wait_for(state="attached", timeout=10000)
        self.page.wait_for_timeout(500)
        confirm_btn.click(force=True, timeout=10000)
        self.page.wait_for_timeout(2000)
        logger.info("弹窗: 已点击确定")

    def assert_create_success(self):
        """断言创建成功"""
        logger.info("断言: 等待'创建成功'提示...")
        success_tip = self.page.locator(
            "[class*='message'], [class*='toast'], [class*='notification'], [class*='tip']"
        ).filter(has_text="创建成功")
        success_tip.first.wait_for(state="visible", timeout=120000)
        logger.info("断言: '创建成功'提示已出现")

    def get_first_instruction_no(self):
        """获取列表第一行第一列的指令编号（按列标题文本定位，不依赖colid）"""
        pane = self.transfer_in_pane
        # 找到"指令编号"列标题的索引
        idx = pane.evaluate("""() => {
            const pane = document.querySelector('#pane-ins-receipt-transfer-in');
            if (!pane) return -1;
            const headers = pane.querySelectorAll('.vxe-header--row th .vxe-cell--title span');
            for (let i = 0; i < headers.length; i++) {
                if (headers[i].textContent.trim() === '指令编号') return i;
            }
            return -1;
        }""")
        if idx == -1:
            raise RuntimeError("未找到'指令编号'列")

        # 取第一行数据
        no = pane.evaluate(f"""() => {{
            const pane = document.querySelector('#pane-ins-receipt-transfer-in');
            if (!pane) return null;
            const rows = pane.querySelectorAll('.vxe-body--row');
            if (rows.length === 0) return null;
            const cells = rows[0].querySelectorAll('.vxe-body--column');
            if (cells.length <= {idx}) return null;
            return cells[{idx}].textContent.trim();
        }}""")
        logger.info(f"获取指令编号: {no}")
        return no

    def execute_full_add(self):
        """执行完整的仓单转入新增流程"""
        self.navigate_and_open_add()
        self.click_add_detail()
        self.fill_detail_form()
        self.click_detail_confirm()
        self.click_main_confirm()
        self.assert_create_success()

        # 等待列表刷新，获取指令编号
        self.page.wait_for_timeout(3000)
        instruction_no = self.get_first_instruction_no()
        logger.info(f"仓单转入新增成功，指令编号: {instruction_no}")
        return instruction_no

    # ==================== 审批相关方法 ====================

    def navigate_and_search_by_instruction_no(self, instruction_no, navigate=True):
        """
        搜索指令编号
        :param instruction_no: 指令编号
        :param navigate: 是否需要先导航到仓单转入tab，默认True
        """
        if navigate:
            logger.info("导航: 点击'货权运营'")
            self.cargo_ops_menu.click()
            time.sleep(0.5)

            logger.info("导航: 点击'货权指令执行'")
            self.cargo_instruction_menu.click()
            time.sleep(2)

            logger.info("Tab: 切换到'仓单转入'")
            self.transfer_in_tab.click()
            time.sleep(2)

        # 输入指令编号搜索
        logger.info(f"搜索: 输入指令编号 '{instruction_no}'")
        search_input = self.transfer_in_pane.locator("input[name='instructionNo']")
        search_input.fill(str(instruction_no))
        self.page.wait_for_timeout(500)

        search_btn = self.transfer_in_pane.locator("button").filter(has_text="搜索")
        search_btn.click()
        self.page.wait_for_timeout(3000)
        logger.info("搜索: 已点击搜索")

    def _click_action_button(self, button_text):
        """点击操作列中的指定按钮（如"货权管理部复核"）"""
        logger.info(f"操作: 点击操作列'{button_text}'")
        btn = self.transfer_in_pane.locator("a.el-link").filter(has_text=button_text).first
        btn.wait_for(state="attached", timeout=10000)
        self.page.wait_for_timeout(500)
        btn.click(force=True, timeout=10000)
        self.page.wait_for_timeout(2000)
        logger.info(f"操作: 已点击'{button_text}'")

    def _approve(self, opinion_text):
        """审批弹窗处理：清空默认值→输入审核意见→点击审核通过→断言操作成功"""
        logger.info(f"审批: 输入审核意见'{opinion_text}'")

        # 定位审批弹窗
        dialog = self.page.locator('.el-dialog').last
        try:
            dialog.wait_for(state="visible", timeout=10000)
        except Exception:
            dialog = self.page.locator('.el-overlay-message-box').last
            dialog.wait_for(state="visible", timeout=10000)

        # 定位审核意见 textarea
        opinion_item = dialog.locator(".el-form-item__label:has-text('审核意见')").locator(
            "xpath=ancestor::div[contains(@class,'el-form-item')]"
        )
        opinion_input = opinion_item.locator("textarea")
        opinion_input.wait_for(state="attached", timeout=5000)

        # 先清空默认值（"同意"），再输入新意见
        opinion_input.click()
        self.page.wait_for_timeout(300)
        opinion_input.fill("")
        self.page.wait_for_timeout(300)
        opinion_input.fill(opinion_text)
        self.page.wait_for_timeout(500)
        logger.info(f"审批: 已输入意见'{opinion_text}'")

        # 点击审核通过
        logger.info("审批: 点击'审核通过'")
        approve_btn = dialog.locator("button:has-text('审核通过')")
        approve_btn.wait_for(state="attached", timeout=5000)
        self.page.wait_for_timeout(500)
        approve_btn.click(force=True, timeout=10000)
        self.page.wait_for_timeout(2000)
        logger.info("审批: 已点击审核通过")

        # 断言"操作成功"
        self._assert_operation_success()

    def _assert_operation_success(self):
        """断言操作成功提示"""
        logger.info("断言: 等待'操作成功'提示...")
        success_tip = self.page.locator(
            "[class*='message'], [class*='toast'], [class*='notification'], [class*='tip']"
        ).filter(has_text="操作成功")
        success_tip.first.wait_for(state="visible", timeout=120000)
        logger.info("断言: '操作成功'提示已出现")

    def _assert_status_completed(self):
        """断言列表第一条数据的状态为'已完成'"""
        logger.info("断言: 检查状态是否为'已完成'")
        self.page.wait_for_timeout(2000)
        # 按列标题"状态"定位列索引
        pane = self.transfer_in_pane
        idx = pane.evaluate("""() => {
            const pane = document.querySelector('#pane-ins-receipt-transfer-in');
            if (!pane) return -1;
            const headers = pane.querySelectorAll('.vxe-header--row th .vxe-cell--title span');
            for (let i = 0; i < headers.length; i++) {
                if (headers[i].textContent.trim() === '状态') return i;
            }
            return -1;
        }""")
        if idx == -1:
            raise RuntimeError("未找到'状态'列")

        status_text = pane.evaluate(f"""() => {{
            const pane = document.querySelector('#pane-ins-receipt-transfer-in');
            if (!pane) return null;
            const rows = pane.querySelectorAll('.vxe-body--row');
            if (rows.length === 0) return null;
            const cells = rows[0].querySelectorAll('.vxe-body--column');
            if (cells.length <= {idx}) return null;
            return cells[{idx}].textContent.trim();
        }}""")
        logger.info(f"状态值: {status_text}")
        assert status_text == "已完成", f"状态不是'已完成'，而是'{status_text}'"
        logger.info("断言: 状态已显示'已完成'")
        save_screenshot(self.page, "仓单转入审批完成")

    def execute_full_approval(self, instruction_no):
        """执行完整的仓单转入审批流程"""
        self.navigate_and_search_by_instruction_no(instruction_no)
        self._click_action_button("货权管理部复核")
        self._approve("货权管理部复核通过")
        # 页面已在仓单转入tab，直接搜索查看状态，不需重新导航
        self.navigate_and_search_by_instruction_no(instruction_no, navigate=False)
        self._assert_status_completed()
        return True
