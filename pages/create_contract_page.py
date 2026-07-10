"""
Author: 章豹
Description: 新增合同页面操作方法
Date: 2026/7/6 17:30
LastEditTime: 2026/7/6 17:30
"""
import time
from pages.public_operation import repetitive_operation, get_row_cell_by_header, fill_cell
from utils.log_print import get_logger
from utils.save_screenshot import save_screenshot


class CreateContractPage:
    def __init__(self, page):
        self.page = page
        #  基础信息元素
        self.contract_management_menu = page.locator("text=合同管理")
        self.contract_bookkeeping_menu = page.locator("text=合同簿记")
        self.transaction_type = page.get_by_role("combobox")
        self.spot_or_forward = page.locator("[id='spotOrForward']")
        self.custormerid = page.locator("[id='customerId']")
        self.bankaccountno = page.locator("[id='bankAccountNo']")
        self.varityid = page.locator("xpath=//input[@id='varietyId']")
        self.userid = page.locator("[id='userUid']")
        self.person = page.locator("[id='person']")
        self.more_or_less_ratio = page.locator("[id='moreOrLessRatio']")
        self.credittype = page.locator("[id='creditType']")
        self.warehouse_receipt_standard = page.locator("[id='warehouseReceiptStandard']")
        self.iscancel = page.locator("[id='isCancel']")
        self.department_leader_user_account = page.locator("[id='departmentLeaderUserAccount']")
        self.business_assistant = page.locator("[id='businessAssistant']")
        #  交付信息元素
        self.paymentorder = page.locator("[id='paymentOrder']")
        self.deliverystartdate = page.locator("[id='deliveryStartDate']")
        self.deliveryenddate = page.locator("[id='deliveryEndDate']")
        self.deliverymethod = page.locator("[id='deliveryMethod']")
        self.forwardername = page.locator("[id='forwarderName']")
        self.warehousefeeby = page.locator("[id='warehouseFeeBy']")
        self.transferfeebear = page.locator("[id='transferFeeBear']")
        self.deliveryfeebear = page.locator("[id='deliveryFeeBear']")
        self.latestpickupdate = page.locator("[id='latestPickupDate']")
        #  付款信息元素
        self.paymentmethod = page.locator("[id='paymentMethod']")
        self.invoicereceiptstartdate = page.locator("[id='invoiceReceiptStartDate']")
        self.invoicereceiptenddate = page.locator("[id='invoiceReceiptEndDate']")
        self.invoicemoneyratio = page.locator("[id='invoiceMoneyRatio']")
        self.invoicemoneyratiostartdate = page.locator("[id='invoiceMoneyRatioStartDate']")
        self.invoicemoneyratioenddate = page.locator("[id='invoiceMoneyRatioEndDate']")
        self.checkratio = page.locator("[id='checkRatio']")
        self.checkratiostartdate = page.locator("[id='checkRatioStartDate']")
        self.checkratioenddate = page.locator("[id='checkRatioEndDate']")
        self.estimatedamountratio = page.locator("[id='estimatedAmountRatio']")
        self.estimatedamountratiostartdate = page.locator("[id='estimatedAmountRatioStartDate']")
        self.estimatedamountratioenddate = page.locator("[id='estimatedAmountRatioEndDate']")
        #  物资明细元素
        self.add_goods_button = page.locator("text=新增物资明细")
        self.warehouse_name = page.locator("input[role='combobox']")
        self.numbers = page.locator("input[role='spinbutton']")
        self.category_name = page.locator("input[role='combobox']")
        self.weight = page.locator("input[role='spinbutton']")
        self.on_call_price = page.locator("input[role='spinbutton']")
        self.basis = page.locator("input[role='spinbutton']")
        self.premiums_and_discounts = page.locator("input[role='spinbutton']")
        self.date_of_manufacture = page.locator("[placeholder='请选择日期']")
        self.warehouse_free_period_start = page.locator("[placeholder='请选择日期']")
        # 报错 & 提交
        self.baocun = page.locator("text=保 存")
        self.tijiao = page.locator("text=提交审批")
    

    def basic_information(self):
        """
        合同簿记-基础信息操作方法
        """
        self.contract_management_menu.click()
        self.contract_bookkeeping_menu.click()
        repetitive_operation(self.page, self.transaction_type, "一口价采购")
        repetitive_operation(self.page, self.spot_or_forward, "即期")
        repetitive_operation(self.page, self.custormerid, "北大方正物产集团有限公司")
        repetitive_operation(self.page, self.bankaccountno, "15-010210", is_click=True)
        repetitive_operation(self.page, self.more_or_less_ratio, "0")
        repetitive_operation(self.page, self.credittype, "客户授信")
        repetitive_operation(self.page, self.warehouse_receipt_standard, "非标准", is_click=True)
        repetitive_operation(self.page, self.iscancel, "否")
        repetitive_operation(self.page, self.department_leader_user_account, "张晶晶")
        repetitive_operation(self.page, self.business_assistant, "ceshizb")
        repetitive_operation(self.page, self.varityid, "硅铁")
        repetitive_operation(self.page, self.userid, "许泽源")
        repetitive_operation(self.page, self.person, "匡毓岚")

    def delivery_information(self):
        """
        合同簿记-交付信息操作方法
        """
        repetitive_operation(self.page, self.paymentorder, "先货后款")
        repetitive_operation(self.page, self.deliverystartdate, "2026-06-01", is_click=True)
        repetitive_operation(self.page, self.deliveryenddate, "2026-06-09", is_click=True)
        repetitive_operation(self.page, self.deliverymethod, "货转", is_click=True)
        repetitive_operation(self.page, self.forwardername, "测试公司", is_click=True)
        repetitive_operation(self.page, self.warehousefeeby, "德睿承担")
        repetitive_operation(self.page, self.transferfeebear, "德睿承担")
        repetitive_operation(self.page, self.deliveryfeebear, "德睿承担")
        repetitive_operation(self.page, self.latestpickupdate, "2026-07-09", is_click=True)
    
    def pricing_information(self):
        """
        合同簿记-点价信息操作方法
        """
        pass

    def payment_information(self):
        """
        合同簿记-付款信息操作方法
        """
        repetitive_operation(self.page, self.paymentmethod, "现汇", is_click=True)
        repetitive_operation(self.page, self.invoicereceiptstartdate, "2026-07-01", is_click=True)
        repetitive_operation(self.page, self.invoicereceiptenddate, "2026-07-10", is_click=True)
        repetitive_operation(self.page, self.invoicemoneyratio, "0", is_click=True)
        repetitive_operation(self.page, self.invoicemoneyratiostartdate, "2026-07-01", is_click=True)
        repetitive_operation(self.page, self.invoicemoneyratioenddate, "2026-07-10", is_click=True)
        repetitive_operation(self.page, self.checkratio, "0", is_click=True)
        repetitive_operation(self.page, self.checkratiostartdate, "2026-07-01", is_click=True)
        repetitive_operation(self.page, self.checkratioenddate, "2026-07-10", is_click=True)
        repetitive_operation(self.page, self.estimatedamountratio, "100", is_click=True)
        repetitive_operation(self.page, self.estimatedamountratiostartdate, "2026-07-01", is_click=True)
        repetitive_operation(self.page, self.estimatedamountratioenddate, "2026-07-10", is_click=True)
    
    def goods_information(self):
        """
        合同簿记-物资信息操作方法
        """
        self.add_goods_button.click()
        new_row = self.page.locator("table tbody tr:last-child") #  定位新增行
        warehouse_name = get_row_cell_by_header(self.page, new_row, "仓库名")
        fill_cell(self.page, warehouse_name, "上海象屿钢铁供应链有限公司（上海象屿钢铁宝山库）",field_type='combobox')
        numbers = get_row_cell_by_header(self.page, new_row, "件数")
        fill_cell(self.page, numbers, "100",field_type='spinbutton')
        category_name = get_row_cell_by_header(self.page, new_row, "品名*")
        fill_cell(self.page, category_name, "硅铁",field_type='combobox')
        weight = get_row_cell_by_header(self.page, new_row, "总重量 *")
        fill_cell(self.page, weight, "100",field_type='spinbutton')
        on_call_price = get_row_cell_by_header(self.page, new_row, "点价成交价*")
        fill_cell(self.page, on_call_price, "10",field_type='spinbutton')
        basis = get_row_cell_by_header(self.page, new_row, "基差 *")
        fill_cell(self.page, basis, "0",field_type='spinbutton')
        premiums_and_discounts = get_row_cell_by_header(self.page, new_row, "升贴水 *")
        fill_cell(self.page, premiums_and_discounts, "0",field_type='spinbutton')
        date_of_manufacture = get_row_cell_by_header(self.page, new_row, "生产日期")
        fill_cell(self.page, date_of_manufacture, "2026-07-10",field_type='datepicker')
        warehouse_free_period_start = get_row_cell_by_header(self.page, new_row, "仓储费起始日")
        fill_cell(self.page, warehouse_free_period_start, "today",field_type='datepicker')

    def create_contract(self):
        """
        新增合同
        """
        self.basic_information()
        self.delivery_information()
        self.payment_information()
        self.goods_information()
        self.baocun.click()
