
import time
from pages.public_operation import repetitive_operation, get_row_cell_by_header, fill_cell
from utils.log_print import get_logger
from utils.save_screenshot import save_screenshot


class ApprovalPage():

    def __init__(self, page):
        self.page = page
        self.submit_approval = page.locator("text=提交审批")
        self.comments = page.locator("[id='comments']")
        self.shenpi = page.locator("text=审 批")
        self.trader_approval = page.locator("text=业务员")
        self.cargo_right_management_2 = page.locator("text=货权管理部复核")
        self.alert_sub = page.locator("xpath=//div[text()='是否提交审批']/../..//span[text()='确 定']")
        # 进入合同详情
        self.contract_management_menu = page.locator("text=合同管理")
        self.contract_bookkeeping_menu = page.locator("text=合同簿记")
        self.search_contract = page.locator("#search[placeholder='请输入合约编号']")
        self.search = page.locator("xpath=//button[@class='ant-btn ant-btn-primary ant-input-search-button']")
    

    def sub_approval(self):
        self.submit_approval.click()
        self.alert_sub.click()

    def get_contract_details(self, contract_code):
        """
        获取合同详情
        """
        self.contract_management_menu.click()
        self.contract_bookkeeping_menu.click()
        get_logger().info(f"查询合同号：{contract_code}")
        self.search_contract.fill(contract_code)
        self.search.click()
        time.sleep(1)


    def public_approval(self, ele_page, conment=None):
        """
        公共审批操作
        点击节点审批按钮，弹窗出来之后输入审批意见，然后提交
        """
        ele_page.click()
        self.comments.fill(conment)
        self.shenpi.click()
        time.sleep(2)

    def approval_process(self, approval_type, contract_code):
        """
        审批流程操作,根据审批类型进行审批操作，分别为合同创建审批补录审批流程，合同创建普通审批流程，买卖交割合同创建审批流程
        """
        self.get_contract_details(contract_code)
        self.sub_approval()
        if approval_type == "补录":
            self.public_approval(self.trader_approval, "业务员审批通过意见")
            self.public_approval(self.cargo_right_management_2, "货权管理部复核通过意见")
        else:
            get_logger().error(f"不支持的审批类型: {approval_type}")
            raise ValueError(f"不支持的审批类型: {approval_type}")
       
