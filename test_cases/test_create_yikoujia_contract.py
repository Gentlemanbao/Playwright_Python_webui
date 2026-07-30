"""
Author: 章豹
Description: 新增合同测试用例
Date: 2026/7/6 17:30
LastEditTime: 2026/7/6 17:30
"""
import pytest
from playwright.sync_api import expect
from playwright.sync_api._generated import Page
from pages.login_page import LoginPage
from pages.approval_page import ApprovalPage
from utils.save_screenshot import save_screenshot
from pages.create_contract_page import CreateContractPage
from utils.log_print import get_logger
from utils.wait_utils import wait_for_text_change

class TestContract():
        contract_code = None  # 类属性，用于跨测试方法共享数据

        # @pytest.mark.skip(reason="跳过新增合同测试")
        @pytest.mark.run(order=1)
        def test_add_contract(self, page, host):
            """
            新增合同
            """
            login_page = LoginPage(page)
            login_page.login(host=host)
            create_contract_page = CreateContractPage(page)
            create_contract_page.create_contract()
            locator = page.locator("#logicContractCode")
            expect(locator).not_to_have_value("")
            TestContract.contract_code = locator.get_attribute("value")  # 使用类属性
            get_logger().info(f"新建合同号：{TestContract.contract_code}")
            save_screenshot(page, "create_contract.png")

        @pytest.mark.run(order=2)
        def test_yikouj_approval(self, page, host):
            """
            新增合同一口价采购合同-审批
            """
            login_page = LoginPage(page)
            login_page.login(host=host)
            approval_page = ApprovalPage(page)
            contract_code = TestContract.contract_code  # 从类属性读取
            approval_page.approval_process("补录", contract_code)
            # 使用轮询等待检测文本变化
            container = page.locator("h3")
            approval_result = wait_for_text_change(
                container, 
                "审核通过", 
                timeout=30000,  # 最多等待30秒
                interval=500    # 每0.5秒检查一次
            )
            save_screenshot(page, "审批结果")
            assert approval_result, f"审批失败，合同号: {contract_code}，未检测到'审核通过'文本" 
        
