# -*- coding: utf-8 -*-
"""
Author: 章豹
Date: 2026-10-23

收票指令创建页面对象
覆盖：财务运营→发票指令执行→收票tab→新增收票指令→填写信息→选择合同→提交
"""
import time
import random
import re
from datetime import datetime
from utils.log_print import get_logger
from utils.save_screenshot import save_screenshot

logger = get_logger()


class ReceiptInstructionCreatePage:
    """收票指令创建页面"""

    def __init__(self, page):
        self.page = page

        # ===== 菜单导航 =====
        self.finance_ops_menu = page.locator(".vben-sub-menu:has-text('财务运营')")
        self.invoice_instruction_menu = page.locator(".vben-menu-item__content:has-text('发票指令执行')")

        # ===== 收票 tab（默认就在收票tab） =====
        self.receipt_pane = page.locator("#pane-ins-receipt")

        # ===== 新增按钮 =====
        self.add_btn = page.locator("button.el-button--primary.el-button--small").filter(has_text=re.compile(r"新增")).first

        # ===== 创建弹窗 =====
        self.create_dialog = page.locator(".el-dialog").last

    def _execute_step(self, step_name, fn):
        """执行单个步骤，报错时自动截图并抛出"""
        try:
            return fn()
        except Exception as e:
            save_screenshot(self.page, f"失败_{step_name}")
            logger.error(f"❌ 步骤 [{step_name}] 执行失败: {e}")
            raise RuntimeError(f"步骤 [{step_name}] 失败: {e}") from e

    def navigate(self):
        """导航到财务运营→发票指令执行（默认在收票tab）"""
        logger.info("导航: 点击'财务运营'")
        self.finance_ops_menu.click()
        time.sleep(0.5)

        logger.info("导航: 点击'发票指令执行'")
        self.invoice_instruction_menu.click()
        time.sleep(2)
        logger.info("导航: 已进入发票指令执行页面（默认收票tab）")

    def click_add(self):
        """点击新增按钮，打开收票指令创建弹窗"""
        logger.info("新增: 点击'新增'按钮")
        self.add_btn.wait_for(state="attached", timeout=15000)
        self.add_btn.click(force=True, timeout=10000)
        self.page.wait_for_timeout(2000)
        logger.info("新增: 已点击新增，等待弹窗打开")

    def fill_creation_form(self, customer_name, invoice_no, invoice_type="增值税电子专用发票"):
        """填写收票指令创建表单"""
        dialog = self.create_dialog
        dialog.wait_for(state="visible", timeout=10000)
        logger.info("表单: 弹窗已打开")

        # 1. 客户名称（el-select）
        logger.info(f"表单: 选择客户名称 '{customer_name}'")
        customer_select = dialog.locator(".el-form-item__label:has-text('客户名称')").locator(
            "xpath=ancestor::div[contains(@class,'el-form-item')]"
        ).locator(".el-select").first
        customer_select.click()
        self.page.wait_for_timeout(500)
        customer_input = customer_select.locator("input")
        customer_input.fill(customer_name)
        self.page.wait_for_timeout(1000)
        customer_input.press("ArrowDown")
        self.page.wait_for_timeout(300)
        customer_input.press("Enter")
        self.page.wait_for_timeout(500)
        logger.info("表单: 客户名称已选择")

        # 2. 发票号
        logger.info(f"表单: 输入发票号 '{invoice_no}'")
        invoice_no_input = dialog.locator(".el-form-item__label:has-text('发票号')").locator(
            "xpath=ancestor::div[contains(@class,'el-form-item')]"
        ).locator("input")
        invoice_no_input.fill(invoice_no)
        logger.info("表单: 发票号已输入")

        # 3. 发票类型（el-select）
        logger.info(f"表单: 选择发票类型 '{invoice_type}'")
        invoice_type_select = dialog.locator(".el-form-item__label:has-text('发票类型')").locator(
            "xpath=ancestor::div[contains(@class,'el-form-item')]"
        ).locator(".el-select").first
        invoice_type_select.click()
        self.page.wait_for_timeout(500)
        type_option = self.page.locator(".el-select-dropdown__item").filter(has_text=invoice_type).first
        type_option.wait_for(state="visible", timeout=5000)
        type_option.click()
        self.page.wait_for_timeout(500)
        logger.info("表单: 发票类型已选择")

        # 4. 发票日期（当天）
        today = datetime.now().strftime("%Y-%m-%d")
        logger.info(f"表单: 输入发票日期 '{today}'")
        date_input = dialog.locator(".el-form-item__label:has-text('发票日期')").locator(
            "xpath=ancestor::div[contains(@class,'el-form-item')]"
        ).locator("input")
        date_input.fill(today)
        self.page.wait_for_timeout(500)
        logger.info("表单: 发票日期已输入")

    def click_add_detail(self):
        """点击新增按钮（打开合同查询弹窗）"""
        logger.info("明细: 点击'新增'按钮打开查询弹窗")
        # 在弹窗内找"新增"按钮
        dialog = self.create_dialog
        add_detail_btn = dialog.locator("button").filter(has_text=re.compile(r"新增")).last
        add_detail_btn.wait_for(state="attached", timeout=10000)
        add_detail_btn.click(force=True, timeout=10000)
        self.page.wait_for_timeout(2000)
        logger.info("明细: 已点击新增，等待查询弹窗")

    def search_and_select_contract(self, contract_code):
        """合同查询弹窗：定位→等表格初始化→输入→查询→验证→勾选→确定"""
        # === 第1步：JS 扫描定位查询弹窗 nth index ===
        # Playwright 的 .filter(has=...) + .last 链式 locator 对多嵌套弹窗不稳定，
        # 用 JS 先确定哪个 .el-dialog 同时包含 "合同号" label + "查询" 按钮 → 就是查询弹窗
        query_idx = self.page.evaluate("""() => {
            let dlgs = document.querySelectorAll('.el-dialog');
            for (let i = 0; i < dlgs.length; i++) {
                let dlg = dlgs[i];
                let labels = [...dlg.querySelectorAll('.el-form-item__label')].map(l => (l.innerText||'').trim());
                let btns = [...dlg.querySelectorAll('button')]
                    .map(b => (b.innerText||'').trim()).filter(t => t);
                if (labels.some(l => l.includes('合同号')) && btns.includes('查询')) {
                    return i;
                }
            }
            return -1;
        }""")
        if query_idx == -1:
            raise RuntimeError("未找到包含'合同号'label+'查询'按钮的弹窗")
        logger.info(f"查询: 查询弹窗 nth={query_idx}")

        query_dialog = self.page.locator(".el-dialog").nth(query_idx)
        query_dialog.wait_for(state="visible", timeout=15000)

        # === 第2步：等 vxe-table 初始化完成（关键！） ===
        # 弹窗打开时 vxe-table 要加载 2901 条默认数据，期间查询按钮点击会被初始化请求覆盖。
        # 判断标准：".vxe-body--row" 首行出现 且 "全选"按钮不再 disabled（加载完成后才 enabled）
        logger.info("查询: 等待 vxe-table 初始数据加载完成...")
        init_ok = False
        for _ in range(30):  # 最多等 30 秒
            try:
                first_row = query_dialog.locator(".vxe-body--row").first
                if first_row.count() > 0:
                    # 再检查 "全选" 按钮是否已 enabled（不包含 is-disabled 类）
                    select_all_btn = query_dialog.locator("button:has-text('全选')").first
                    if select_all_btn.count() > 0:
                        classes = select_all_btn.get_attribute("class") or ""
                        if "is-disabled" not in classes:
                            init_ok = True
                            break
            except Exception:
                pass
            self.page.wait_for_timeout(1000)

        if not init_ok:
            # 兜底：只要有行出现就算初始化完成
            try:
                query_dialog.locator(".vxe-body--row").first.wait_for(state="visible", timeout=5000)
                logger.warning("查询: 全选按钮仍 disabled 但表格行已出现，继续执行")
            except Exception:
                raise RuntimeError("vxe-table 初始数据 30 秒内未加载完成")
        logger.info("查询: ✅ vxe-table 初始数据已加载")

        # === 第3步：输入合同号 ===
        logger.info(f"查询: 输入合同号 '{contract_code}'")
        contract_input = query_dialog.locator(".el-form-item__label:has-text('合同号')").locator(
            "xpath=ancestor::div[contains(@class,'el-form-item')]"
        ).locator("input")
        contract_input.click()
        self.page.wait_for_timeout(300)
        contract_input.fill(str(contract_code))
        self.page.wait_for_timeout(500)
        # blur 触发 Element Plus el-input 的 change/input 事件，更新查询表单 model
        contract_input.evaluate("el => el.blur()")
        self.page.wait_for_timeout(500)
        logger.info("查询: 合同号已输入")

        # === 第4步：点击查询按钮 ===
        # 查询按钮在弹窗顶部查询表单区（不在 .el-dialog__footer），
        # 用最简单的 :has-text 定位（和 purchase_claim_page 成功案例一致）
        logger.info("查询: 点击查询按钮")
        query_dialog.locator("button:has-text('查询')").first.click(force=True, timeout=15000)
        self.page.wait_for_timeout(2000)  # 给 Vue 一个重渲染的时间
        logger.info("查询: 已点击查询")

        # === 第5步：严格门控——轮询验证查询生效（后端查询慢，不能只等一次） ===
        logger.info("查询: 轮询验证查询结果是否包含目标合同号...")
        deadline = time.time() + 20  # 最多等 20 秒
        found = False
        row_text = ""
        while time.time() < deadline:
            try:
                first_row = query_dialog.locator(".vxe-body--row").first
                if first_row.count() > 0:
                    row_text = first_row.inner_text()
                    if str(contract_code) in row_text:
                        found = True
                        break
            except Exception:
                pass
            self.page.wait_for_timeout(500)

        logger.info(f"查询: 首行文本='{row_text[:150]}'")
        if not found:
            dump = self.page.evaluate("""(nthIdx) => {
                let rows = document.querySelectorAll('.el-dialog')[nthIdx]?.querySelectorAll('.vxe-body--row') || [];
                return [...rows].slice(0, 5).map(r => (r.innerText||'').substring(0, 200));
            }""", query_idx)
            raise RuntimeError(f"查询未生效！合同号 '{contract_code}' 未出现在结果中。前5行: {dump}")
        logger.info(f"查询: ✅ 过滤成功，首行包含 '{contract_code}'")

        # === 第6步：勾选全选 checkbox ===
        logger.info("查询: 勾选表头全选")
        header_checkbox = query_dialog.locator(".vxe-header--row .vxe-cell--checkbox").first
        header_checkbox.wait_for(state="attached", timeout=10000)
        header_checkbox.click(force=True, timeout=10000)
        self.page.wait_for_timeout(1000)

        # === 第7步：点击确定 ===
        logger.info("查询: 点击确定")
        query_dialog.locator(".el-dialog__footer button:has-text('确定')").click(force=True, timeout=10000)
        self.page.wait_for_timeout(3000)
        logger.info("查询: 已点击确定，等待弹窗关闭")

    def fill_invoice_amount_from_receipt(self):
        """从收票信息表格的合计行提取收票金额汇总值，填入发票金额"""
        logger.info("金额: 从合计行提取收票金额汇总值")
        dialog = self.create_dialog
        dialog.wait_for(state="visible", timeout=10000)

        # 找到收票信息表格（收票金额在这个表格里）
        table = dialog.locator(".vxe-table").nth(1)  # 第二个 vxe-table（第一个是"未收发票"，第二个是"收票信息"）
        try:
            table.wait_for(state="attached", timeout=10000)
        except Exception:
            # 兜底：如果只有一个表格，就取第一个
            table = dialog.locator(".vxe-table").first
            logger.warning("金额: 只找到一个 vxe-table，使用第一个")

        # 用 JS 提取合计行"收票金额"列的值
        # vxe-table 合计行：可能是 .vxe-footer--row（固定底部）或 .vxe-body--row__summary
        # 按列头名定位到对应 colid，再从合计行同 colid 的 td 里取文本
        amount_text = self.page.evaluate("""(tableEl) => {
            if (!tableEl) return null;
            // 1. 从表头找"收票金额"列的 colid
            let headerCells = tableEl.querySelectorAll('.vxe-header--row th');
            let targetColid = null;
            for (let th of headerCells) {
                let headerText = th.innerText || '';
                if (headerText.includes('收票金额')) {
                    targetColid = th.getAttribute('colid') || th.getAttribute('data-colid');
                    break;
                }
            }
            if (!targetColid) return null;

            // 2. 从合计行找该 colid 对应的单元格（可能在 footer 或 body summary 行）
            let summaryRow = tableEl.querySelector('.vxe-footer--row, .vxe-body--row__summary, .vxe-body--row.is--summary');
            if (!summaryRow) {
                // 兜底：找文本含"合计"的行
                let rows = tableEl.querySelectorAll('.vxe-body--row');
                for (let r of rows) {
                    if ((r.innerText || '').includes('合计')) { summaryRow = r; break; }
                }
            }
            if (!summaryRow) return null;

            // 3. 在合计行里按 colid 找 td
            let cell = summaryRow.querySelector(`td[colid="${targetColid}"], td[data-colid="${targetColid}"]`);
            if (!cell) {
                // 兜底：按列索引——找表头第几列是收票金额，取合计行同索引的 td
                let allTh = tableEl.querySelectorAll('.vxe-header--row th');
                let colIdx = -1;
                for (let i = 0; i < allTh.length; i++) {
                    if ((allTh[i].innerText || '').includes('收票金额')) { colIdx = i; break; }
                }
                let allTd = summaryRow.querySelectorAll('td');
                if (colIdx >= 0 && colIdx < allTd.length) {
                    cell = allTd[colIdx];
                }
            }
            if (!cell) return null;
            // 取文本，去掉千分位逗号和空白
            return (cell.innerText || cell.textContent || '').replace(/,/g, '').trim();
        }""", table.element_handle())

        if not amount_text:
            # 兜底：直接取收票金额输入框的值（多条时只有第一条，标注 warning）
            logger.warning("金额: 未从合计行提取到值，兜底取第一条明细的收票金额")
            receipt_amount_input = dialog.locator(".vxe-table input[role='spinbutton']").first
            receipt_amount_input.wait_for(state="attached", timeout=10000)
            amount_text = receipt_amount_input.input_value()

        logger.info(f"金额: 合计行提取到收票金额汇总值 '{amount_text}'")

        # 填入发票金额
        invoice_amount_input = dialog.locator(".el-form-item__label:has-text('发票金额')").locator(
            "xpath=ancestor::div[contains(@class,'el-form-item')]"
        ).locator("input")
        invoice_amount_input.fill(str(amount_text))
        self.page.wait_for_timeout(500)
        logger.info(f"金额: 发票金额已填入 '{amount_text}'")
        return amount_text

    def click_confirm(self):
        """点击确定按钮提交"""
        logger.info("提交: 点击'确定'")
        dialog = self.create_dialog
        confirm_btn = dialog.locator("button").filter(has_text=" 确定 ")
        confirm_btn.wait_for(state="attached", timeout=5000)
        confirm_btn.click(force=True, timeout=10000)
        self.page.wait_for_timeout(2000)
        logger.info("提交: 已点击确定")

    def assert_create_success(self):
        """断言创建成功提示"""
        logger.info("断言: 等待'创建成功'提示...")
        success_tip = self.page.locator(
            "[class*='message'], [class*='toast'], [class*='notification'], [class*='tip']"
        ).filter(has_text="创建成功")
        success_tip.first.wait_for(state="visible", timeout=120000)
        assert success_tip.count() > 0, "未检测到'创建成功'提示"
        logger.info("断言: '创建成功'提示已出现")
        save_screenshot(self.page, "收票指令创建成功")
        return True

    def execute_create_receipt_instruction(self, contract_code, customer_name):
        """执行完整的收票指令创建流程"""
        invoice_no = ''.join(random.choices('0123456789', k=8))

        steps = [
            ("01_navigate", lambda: self.navigate()),
            ("02_click_add", lambda: self.click_add()),
            ("03_fill_form", lambda: self.fill_creation_form(customer_name, invoice_no)),
            ("04_click_add_detail", lambda: self.click_add_detail()),
            ("05_search_select_contract", lambda: self.search_and_select_contract(contract_code)),
            ("06_fill_amount", lambda: self.fill_invoice_amount_from_receipt()),
            ("07_click_confirm", lambda: self.click_confirm()),
            ("08_assert_success", lambda: self.assert_create_success()),
        ]
        for step_name, step_fn in steps:
            self._execute_step(step_name, step_fn)
        return True
