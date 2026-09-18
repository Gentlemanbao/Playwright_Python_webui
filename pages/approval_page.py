
import re
import time
from utils.log_print import get_logger


class ApprovalPage():

    def __init__(self, page):
        self.page = page
        # 提交审批：页面同时可能有"提交审批"等按钮，精确匹配
        self.submit_approval = page.locator("button").filter(has_text=re.compile(r"^\s*提交审批\s*$"))
        # 提交审批后的确认框是 el-popconfirm（"是否提交审批 取消 确定"），
        # 既不是 el-message-box 也不是 el-dialog，必须把它一起纳入匹配
        self.alert_sub = page.locator(
            ".el-popconfirm button, .el-message-box button, .el-dialog button"
        ).filter(has_text=re.compile(r"^\s*确定\s*$")).first
        # 进入合同详情 (Vue Vben Admin)
        self.contract_management_menu = page.locator(".vben-sub-menu:has-text('合同管理')")
        self.contract_bookkeeping_menu = page.locator(".vben-menu-item__content:has-text('合同簿记')")
        self.search_contract = page.locator("[placeholder='请输入合约编号']")
        self.search = page.locator("button:has-text('搜索')")

        # 审批节点按钮（合同详情页顶部工具栏）
        self.trader_approval = page.locator("button").filter(has_text=re.compile(r"^\s*业务员\s*$")).first
        self.cargo_right_management_2 = page.locator("button").filter(has_text=re.compile(r"^\s*货权管理部复核\s*$")).first

    def sub_approval(self):
        """提交审批并确认"""
        self.submit_approval.first.click()
        self.alert_sub.wait_for(state="visible", timeout=8000)
        self.alert_sub.click()
        time.sleep(2)

    def get_contract_details(self, contract_code):
        """
        获取合同详情
        注意：点击"合同簿记"菜单在 tab 已存在时只是切换并**重新挂载**组件，
        刚 fill 进去的合同号会被重建清空（实测第二次调用时搜索框为空、
        查询不到任何合同），因此填完后要校验值是否还在，必要时重填。
        """
        self.contract_management_menu.click()
        self.contract_bookkeeping_menu.click()
        # 等 tab 切换/组件挂载稳定，否则填的值会被随后的重建清掉
        time.sleep(2)
        get_logger().info(f"查询合同号：{contract_code}")
        code = str(contract_code)
        for _ in range(3):
            self.search_contract.fill(code)
            time.sleep(0.5)
            if self.search_contract.input_value() == code:
                break
        self.search.click()
        time.sleep(1)
        # 等详情标题出现（h3 变为"合同簿记 <合同号>-<状态>"）
        h3 = self.page.locator("h3").first
        for _ in range(20):
            try:
                if code in h3.inner_text():
                    break
            except Exception:
                pass
            time.sleep(0.5)

    def public_approval(self, node_button, conment=None):
        """
        公共审批操作
        点击节点审批按钮，弹窗出来之后输入审批意见，然后审批提交。
        注意：审批弹窗是 .el-dialog，意见框是 placeholder='审批意见' 的 textarea
        （没有 name 属性，不能用 [name='comments']），审批按钮须限定在弹窗内精确匹配，
        否则会命中页面的"审批流程/审批退回/审批撤回"等按钮。
        """
        node_button.click()
        dialog = self.page.locator(".el-dialog:visible").last
        dialog.wait_for(state="visible", timeout=10000)
        textarea = dialog.locator("textarea[placeholder='审批意见']").first
        textarea.wait_for(state="visible", timeout=5000)
        textarea.fill(conment or "")
        dialog.locator("button").filter(has_text=re.compile(r"^\s*审批\s*$")).first.click()
        # 等弹窗关闭
        dialog.wait_for(state="hidden", timeout=10000)
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

