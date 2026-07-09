import time
from pages.public_operation import repetitive_operation
from utils.log_print import get_logger
from utils.save_screenshot import save_screenshot


class CreateContractPage:
    def __init__(self, page):
        self.page = page
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
        self.paymentorder = page.locator("[id='paymentOrder']")
        self.deliverystartdate = page.locator("[id='deliveryStartDate']")
        self.deliveryenddate = page.locator("[id='deliveryEndDate']")
        self.deliverymethod = page.locator("[id='deliveryMethod']")
        self.forwardername = page.locator("[id='forwarderName']")
        self.warehousefeeby = page.locator("[id='warehouseFeeBy']")
        self.transferfeebear = page.locator("[id='transferFeeBear']")
        self.deliveryfeebear = page.locator("[id='deliveryFeeBear']")
        self.latestpickupdate = page.locator("[id='latestPickupDate']")

    

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
        repetitive_operation(self.page, self.deliverystartdate, "2026-07-01")
        repetitive_operation(self.page, self.deliveryenddate, "2026-07-09")
        repetitive_operation(self.page, self.deliverymethod, "货转")
        repetitive_operation(self.page, self.forwardername, "测试公司")
        repetitive_operation(self.page, self.warehousefeeby, "德睿承担")
        repetitive_operation(self.page, self.transferfeebear, "德睿承担")
        repetitive_operation(self.page, self.deliveryfeebear, "德睿承担")
        repetitive_operation(self.page, self.latestpickupdate, "2026-07-09")
    
    def create_contract(self):
        """
        新增合同
        """
        self.basic_information()
        self.delivery_information()