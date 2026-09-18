# -*- coding: utf-8 -*-
"""
Author: 章豹
Date: 2026-07-07 13:10:41
LastEditors: Do not edit
LastEditTime: 2026-09-17 10:45:00
FilePath: ui_auto_project/pages/goods_transfer_in_page.py
"""

import time
from pages.public_operation import repetitive_operation


class GoodsTransferInPage:
    def __init__(self, page):
        self.page = page
        # 菜单导航元素 (Vue Vben Admin)
        self.operation_menu = page.locator(".vben-sub-menu:has-text('货权运营')")
        self.cargo_execution_menu = page.locator(".vben-menu-item__content:has-text('货权指令执行')")
        self.transfer_in_menu = page.get_by_text("入库指令", exact=True)
        self.add_transfer_in_button = page.locator("button:has-text('新增')")
        time.sleep(0.5)
        # ======= 主弹窗：新增入库指令 =======
        # 入库方式单选：货转入库
        self.putstorageway = page.locator('div[slot="putStorageWay"]').locator('label.el-radio', has_text="货物入库")
        # 仓库/港口码头 - ENABLED 的 el-select（用 label 锚定）
        # 选中仓库后，仓储供应商、存货地址自动联动填充（disabled el-select）
        self.warehouse_select = self.page.locator(
            "label:has-text('仓库')"
        ).locator("xpath=parent::div//div[contains(@class,'el-select') and not(contains(@class,'el-select__'))]")
        self.varietyid = self.page.locator("[name='varietyId']")
        self.categoryid = self.page.locator("[name='categoryId']")
        # 主弹窗里的"新增"按钮 → 点了弹出嵌套弹窗"货权明细"
        self.add_detail_btn = self.page.locator("button:has-text(' 新增 ')").nth(1)
        # 主弹窗底部按钮
        self.save_btn = self.page.locator("button:has-text('保存')")
        self.confirm_btn = self.page.locator("button:has-text('确认')")
        self.confirm_confirm_btn = self.page.locator("button:has-text('确定')")

    def add_transfer_in(self):
        """
        新增入库指令 - 正确操作流程：
        1. 主弹窗：选入库方式（货转入库）→ 选仓库 → 仓储供应商联动填充
        2. 点"新增" → 弹出嵌套弹窗"货权明细"
        3. 嵌套弹窗：填对方实体、入库日期、品种、品名、重量、数量
        4. 嵌套弹窗确定 → 主弹窗保存
        """
        # ===== 第 1 步：打开主弹窗 =====
        self.operation_menu.click()
        self.cargo_execution_menu.click()
        self.transfer_in_menu.click()
        self.add_transfer_in_button.click()
        self.putstorageway.locator('span.el-radio__label').click(delay=50)
        self.page.wait_for_timeout(200)
        # 选择仓库（enabled el-select）→ 仓储供应商自动联动
        repetitive_operation(self.page, self.warehouse_select, "江苏银海农佳乐仓储有限公司")
        self.page.wait_for_timeout(500)
        # ===== 第 3 步：点新增 → 弹出嵌套弹窗 =====
        self.add_detail_btn.wait_for(state="visible", timeout=5000)
        self.add_detail_btn.click(force=True)
        self.page.wait_for_timeout(800)
        # ===== 第 4 步：填写嵌套弹窗"货权明细" =====
        # 对方实体 - el-select（无 name，通过第一个 enabled el-select 定位）
        # 用 label "对方实体" 锚定
        customer_select = self.page.locator(
            "label:has-text('对方实体')"
        ).locator("xpath=parent::div//div[contains(@class,'el-select') and not(contains(@class,'el-select__'))]")
        repetitive_operation(self.page, customer_select, "北大方正物产集团有限公司", is_click=True)
        # 入库日期 - el-date-editor
        date_editor = self.page.locator("[name='confirmDate']").first.locator(
            "xpath=ancestor::div[contains(@class,'el-date-editor')]"
        )
        date_editor.click()
        # 多个日期面板残留，取第一个可见的
        self.page.locator(".el-picker-panel:visible").first.locator(
            "button:has-text('今天')"
        ).first.click()
        # 品种 - el-select
        repetitive_operation(self.page, self.varietyid, "硅铁", is_click=True)
        # 品名 - el-select
        repetitive_operation(self.page, self.categoryid, "硅铁", is_click=True)
        # 入库重量、入库数量 - 普通 input
        weight_input = self.page.locator("[name='inputWeight']")
        repetitive_operation(self.page, weight_input, "189")
        num_input = self.page.locator("[name='inputNum']")
        repetitive_operation(self.page, num_input, "100")
        # 等待保存完成 + 弹窗关闭
        self.confirm_btn.click()
        self.confirm_confirm_btn.click()
        self.page.wait_for_timeout(1000)
        # ===== 第 7 步：刷新列表（保存后列表可能没自动刷新，点"搜索"按钮重新查询）=====
        # 找到页面上的"搜索"按钮（不是弹窗内的）
        search_btn = self.page.locator("button:has-text('搜索')").first
        if search_btn.count() > 0:
            search_btn.click(force=True)
            self.page.wait_for_timeout(2000)
