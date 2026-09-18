# -*- coding: utf-8 -*-
"""
@Time ： 2026/7/6 17:30
@Auth ： 章豹
@File ：create_contract_page.py
@IDE ：PyCharm
@LastEditTime ： 2026/9/16 17:30
"""
import re
import time
from pages.public_operation import (
    repetitive_operation,
    select_dropdown_option,
    get_vxe_table_by_header,
    vxe_fill_cell,
)


def _ancestor_el_select(locator):
    """根据 name 属性定位 input，再找最外层的 .el-select 组件（避免匹配到嵌套子 div）"""
    return locator.first.locator("xpath=ancestor::div[contains(@class,'el-select') and not(contains(@class,'el-select__'))]")


class CreateContractPage:
    def __init__(self, page):
        self.page = page
        # 菜单导航
        self.contract_management_menu = page.locator(".vben-sub-menu:has-text('合同管理')")
        self.contract_bookkeeping_menu = page.locator(".vben-menu-item__content:has-text('合同簿记')")

        # === 基础信息 ===
        # 交易类型下拉（页面上第一个 el-select）
        self.transaction_type = page.locator(".el-select").first
        # 即期/远期 下拉（Vue el-select，非 radio）
        self.spot_or_forward = _ancestor_el_select(page.locator("[name='spotOrForward']"))
        # 客户名称下拉
        self.custormerid = _ancestor_el_select(page.locator("[name='customerId']"))
        # 银行账户下拉
        self.bankaccountno = _ancestor_el_select(page.locator("[name='bankAccountNo']"))
        # 品种下拉
        self.varityid = _ancestor_el_select(page.locator("[name='varietyId']"))
        # 交易员下拉
        self.userid = _ancestor_el_select(page.locator("[name='userUid']"))
        # 联系人下拉
        self.person = _ancestor_el_select(page.locator("[name='person']"))
        # 溢短比例 text input
        self.more_or_less_ratio = page.locator("[name='moreOrLessRatio']")
        # 授信类型下拉
        self.credittype = _ancestor_el_select(page.locator("[name='creditType']"))
        # 价货顺序下拉
        self.priceorder = _ancestor_el_select(page.locator("[name='priceOrder']"))
        # 仓单标准下拉
        self.warehouse_receipt_standard = _ancestor_el_select(page.locator("[name='warehouseReceiptStandard']"))
        # 是否注销 下拉
        self.iscancel = _ancestor_el_select(page.locator("[name='isCancel']"))
        # 对手合同号 text input
        self.opponentcontractcode = page.locator("[name='opponentContractCode']")
        # 期现部负责人 下拉
        self.department_leader_user_account = _ancestor_el_select(page.locator("[name='departmentLeaderUserAccount']"))
        # 业务助理 下拉
        self.business_assistant = _ancestor_el_select(page.locator("[name='businessAssistant']"))
        # 是否补录 下拉
        self.isrecording = _ancestor_el_select(page.locator("[name='isRecording']"))

        # === 交付信息 ===
        # 价货顺序/先货后款
        self.paymentorder = _ancestor_el_select(page.locator("[name='paymentOrder']"))
        self.deliverystartdate = page.locator("[name='deliveryStartDate']")
        self.deliveryenddate = page.locator("[name='deliveryEndDate']")
        self.deliverymethod = _ancestor_el_select(page.locator("[name='deliveryMethod']"))
        self.forwardername = page.locator("[name='forwarderName']")
        self.warehousefeeby = _ancestor_el_select(page.locator("[name='warehouseFeeBy']"))
        self.transferfeebear = _ancestor_el_select(page.locator("[name='transferFeeBear']"))
        self.deliveryfeebear = _ancestor_el_select(page.locator("[name='deliveryFeeBear']"))
        self.latestpickupdate = page.locator("[name='latestPickupDate']")

        # === 付款信息 ===
        self.paymentmethod = _ancestor_el_select(page.locator("[name='paymentMethod']"))
        self.invoicereceiptstartdate = page.locator("[name='invoiceReceiptStartDate']")
        self.invoicereceiptenddate = page.locator("[name='invoiceReceiptEndDate']")
        self.invoicemoneyratio = page.locator("[name='invoiceMoneyRatio']")
        self.invoicemoneyratiostartdate = page.locator("[name='invoiceMoneyRatioStartDate']")
        self.invoicemoneyratioenddate = page.locator("[name='invoiceMoneyRatioEndDate']")
        self.checkratio = page.locator("[name='checkRatio']")
        self.checkratiostartdate = page.locator("[name='checkRatioStartDate']")
        self.checkratioenddate = page.locator("[name='checkRatioEndDate']")
        self.estimatedamountratio = page.locator("[name='estimatedAmountRatio']")
        self.estimatedamountratiostartdate = page.locator("[name='estimatedAmountRatioStartDate']")
        self.estimatedamountratioenddate = page.locator("[name='estimatedAmountRatioEndDate']")

        # === 物资明细 ===
        self.add_goods_button = page.locator("button:has-text(' 新增物资明细 ')")

        # === 保存/提交 ===
        # 页面上同时有"本地保存"和"保存"，必须精确匹配避免命中"本地保存"
        self.baocun = page.locator("button").filter(has_text=re.compile(r"^\s*保存\s*$"))
        self.tijiao = page.locator("button").filter(has_text=re.compile(r"^\s*提交审批\s*$"))

    def basic_information(self):
        """合同簿记-基础信息"""
        self.contract_management_menu.click()
        self.contract_bookkeeping_menu.click()
        # 先选交易类型，让基础信息表单出现
        repetitive_operation(self.page, self.transaction_type, "一口价采购")
        # 等待基础信息表单渲染
        self.page.wait_for_timeout(1000)
        # 即期/远期 下拉
        repetitive_operation(self.page, self.spot_or_forward, "即期")
        # 下拉选择类字段
        repetitive_operation(self.page, self.custormerid, "北大方正物产集团有限公司")
        repetitive_operation(self.page, self.bankaccountno, "中国光大银行股份有限公司上海分行-35500188069094023")
        # 数字输入
        self.more_or_less_ratio.fill("0")
        # 下拉
        repetitive_operation(self.page, self.credittype, "客户授信")
        repetitive_operation(self.page, self.warehouse_receipt_standard, "非标准")
        # 是否注销 下拉
        repetitive_operation(self.page, self.iscancel, "否")
        # 下拉
        repetitive_operation(self.page, self.department_leader_user_account, "张晶晶")
        repetitive_operation(self.page, self.varityid, "硅铁")
        repetitive_operation(self.page, self.userid, "许泽源")
        repetitive_operation(self.page, self.person, "1")
        # 业务助理 下拉（可搜索，输入关键词过滤后选择）
        select_dropdown_option(self.page, self.business_assistant, "ceshizb", timeout=8000)
        # 是否补录 下拉
        repetitive_operation(self.page, self.isrecording, "是")

    def delivery_information(self):
        """合同簿记-交付信息"""
        repetitive_operation(self.page, self.paymentorder, "先货后款")
        repetitive_operation(self.page, self.deliverystartdate, "2026-06-01", is_click=True)
        repetitive_operation(self.page, self.deliveryenddate, "2026-06-09", is_click=True)
        repetitive_operation(self.page, self.deliverymethod, "货转")
        repetitive_operation(self.page, self.forwardername, "测试公司")
        repetitive_operation(self.page, self.warehousefeeby, "德睿承担")
        repetitive_operation(self.page, self.transferfeebear, "德睿承担")
        repetitive_operation(self.page, self.deliveryfeebear, "德睿承担")
        repetitive_operation(self.page, self.latestpickupdate, "2026-07-09", is_click=True)

    def pricing_information(self):
        """合同簿记-点价信息"""
        pass

    def payment_information(self):
        """合同簿记-付款信息"""
        repetitive_operation(self.page, self.paymentmethod, "现汇")
        repetitive_operation(self.page, self.invoicereceiptstartdate, "2026-07-01", is_click=True)
        repetitive_operation(self.page, self.invoicereceiptenddate, "2026-07-10", is_click=True)
        self.invoicemoneyratio.fill("0")
        repetitive_operation(self.page, self.invoicemoneyratiostartdate, "2026-07-01", is_click=True)
        repetitive_operation(self.page, self.invoicemoneyratioenddate, "2026-07-10", is_click=True)
        self.checkratio.fill("0")
        repetitive_operation(self.page, self.checkratiostartdate, "2026-07-01", is_click=True)
        repetitive_operation(self.page, self.checkratioenddate, "2026-07-10", is_click=True)
        self.estimatedamountratio.fill("100")
        repetitive_operation(self.page, self.estimatedamountratiostartdate, "2026-07-01", is_click=True)
        repetitive_operation(self.page, self.estimatedamountratioenddate, "2026-07-10", is_click=True)

    def goods_information(self):
        """合同簿记-货物信息（vxe-table，点击单元格激活编辑，列虚拟渲染）"""
        self.add_goods_button.click()
        self.page.wait_for_timeout(1500)
        # 表格可能因联动重建，每次填充前都按特征列头重新定位
        table = get_vxe_table_by_header(self.page)
        vxe_fill_cell(self.page, table, "仓库名",
                      "上海象屿钢铁供应链有限公司（上海象屿钢铁宝山库）", field_type='combobox')
        # 选仓库后 存货地址/仓储供应商 联动加载，品名选项依赖仓库，等一会
        self.page.wait_for_timeout(2000)
        table = get_vxe_table_by_header(self.page)
        vxe_fill_cell(self.page, table, "件数", "100", field_type='spinbutton')
        table = get_vxe_table_by_header(self.page)
        vxe_fill_cell(self.page, table, "品名*", "硅铁", field_type='combobox')
        table = get_vxe_table_by_header(self.page)
        vxe_fill_cell(self.page, table, "总重量 *", "100", field_type='spinbutton')
        table = get_vxe_table_by_header(self.page)
        vxe_fill_cell(self.page, table, "点价成交价*", "10", field_type='spinbutton')
        table = get_vxe_table_by_header(self.page)
        vxe_fill_cell(self.page, table, "基差 *", "0", field_type='spinbutton')
        table = get_vxe_table_by_header(self.page)
        vxe_fill_cell(self.page, table, "升贴水 *", "0", field_type='spinbutton')
        table = get_vxe_table_by_header(self.page)
        vxe_fill_cell(self.page, table, "生产日期", "2026-07-10", field_type='datepicker')
        # 注意：原代码的"仓储费起始日"列在表格中不存在（只有"仓储费截止日期"），已移除

    def create_contract(self):
        """新增合同"""
        self.basic_information()
        self.delivery_information()
        self.payment_information()
        self.goods_information()
        self.baocun.click()
        time.sleep(2)
