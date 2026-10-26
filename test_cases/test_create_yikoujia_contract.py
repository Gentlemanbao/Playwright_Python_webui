'''
Author: 章豹
Date: 2026-09-18 09:27:42
LastEditors: Do not edit
LastEditTime: 2026-10-26 10:59:36
'''
# -*- coding: utf-8 -*-
import pytest
from playwright.sync_api import expect
from pages.login_page import LoginPage
from pages.approval_page import ApprovalPage
from pages.purchase_claim_page import PurchaseClaimPage
from pages.payment_request_page import PaymentRequestPage
from pages.payment_instruction_approval_page import PaymentInstructionApprovalPage
from pages.receipt_instruction_create_page import ReceiptInstructionCreatePage
from utils.save_screenshot import save_screenshot
from pages.create_contract_page import CreateContractPage
from pages.public_operation import _el_select_selected_label
from utils.log_print import get_logger
from utils.wait_utils import wait_for_text_change


class TestContract():
    contract_code = None  # 类属性，用于跨测试方法共享数据
    customer_name = None  # 客户名称，用于后续用例

    # @pytest.mark.skip(reason="暂不执行新增合同")
    @pytest.mark.run(order=1)
    def test_add_contract(self, page, host):
        """
        新增合同
        """
        login_page = LoginPage(page)
        login_page.login(host=host)
        create_contract_page = CreateContractPage(page)
        create_contract_page.create_contract()
        locator = page.locator("[name='logicContractCode']")
        save_screenshot(page, "合同创建")
        expect(locator).not_to_have_value("")
        # Vue 双向绑定只更新 value 属性（property），get_attribute 拿不到，必须用 input_value
        TestContract.contract_code = locator.input_value()  # 使用类属性
        get_logger().info(f"新建合同号：{TestContract.contract_code}")

        # 客户名称在 el-select 选中后显示在 .el-select__placeholder 中，
        # [name='customerId'] 存的是客户 ID（数字），不是名称，input_value() 会拿到空/ID
        customer_select = page.locator("[name='customerId']").first.locator(
            "xpath=ancestor::div[contains(@class,'el-select') and not(contains(@class,'el-select__'))]"
        )
        TestContract.customer_name = _el_select_selected_label(customer_select)
        get_logger().info(f"客户名称：{TestContract.customer_name}")
        assert TestContract.customer_name, "客户名称获取为空，后续收票指令用例会失败"
        save_screenshot(page, "create_contract.png")

    # @pytest.mark.skip(reason="暂不执行")
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
        # 审批完成后页面状态不会自动刷新（h3 仍停留在"待审核"），
        # 必须重新查询合同拿到最新状态再断言
        approval_page.get_contract_details(contract_code)
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

    # @pytest.mark.skip(reason="暂不执行")
    @pytest.mark.run(order=3)
    def test_purchase_claim(self, page, host):
        """
        采购货物认领（衔接在审批之后，业务连贯）
        """
        get_logger().info("=== 开始执行：采购货物认领 ===")
        login_page = LoginPage(page)
        login_page.login(host=host)

        contract_code = TestContract.contract_code
        claim_page = PurchaseClaimPage(page)
        save_success = claim_page.execute_purchase_claim(contract_code)

        save_screenshot(page, "采购货物认领完成")
        get_logger().info("=== 采购货物认领执行完毕 ===")

        assert save_success, "采购货物认领保存失败，未检测到成功提示"

    # @pytest.mark.skip(reason="暂不执行")
    @pytest.mark.run(order=4)
    def test_payment_request(self, page, host):
        """
        付款申请：采购货物认领后，对一口价采购合同执行付款申请
        """
        get_logger().info("=== 开始执行：付款申请 ===")
        login_page = LoginPage(page)
        login_page.login(host=host)

        contract_code = TestContract.contract_code
        payment_page = PaymentRequestPage(page)
        result = payment_page.execute_payment_request(contract_code)

        assert result is True, "付款申请执行失败"
        get_logger().info("=== 付款申请执行成功 ===")

    # @pytest.mark.skip(reason="暂不执行")
    @pytest.mark.run(order=5)
    def test_payment_instruction_approval(self, page, host):
        """
        付款指令审批：付款申请后，对生成的指令执行多级审批流程
        （投资经理→财务资金审核→财务总监→执行→断言已完成）
        """
        get_logger().info("=== 开始执行：付款指令审批 ===")
        login_page = LoginPage(page)
        login_page.login(host=host)

        contract_code = TestContract.contract_code
        approval_page = PaymentInstructionApprovalPage(page)
        result = approval_page.execute_full_approval(contract_code)

        assert result is True, "付款指令审批执行失败"
        get_logger().info("=== 付款指令审批执行成功 ===")

    # @pytest.mark.skip(reason="暂不执行")
    @pytest.mark.run(order=6)
    def test_receipt_instruction_create(self, page, host):
        """
        收票指令创建：付款指令审批后，对采购合同创建收票指令
        """
        get_logger().info("=== 开始执行：收票指令创建 ===")
        login_page = LoginPage(page)
        login_page.login(host=host)

        contract_code = TestContract.contract_code
        customer_name = TestContract.customer_name
        receipt_page = ReceiptInstructionCreatePage(page)
        result = receipt_page.execute_create_receipt_instruction(contract_code=contract_code, customer_name=customer_name)

        assert result is True, "收票指令创建失败"
        get_logger().info("=== 收票指令创建执行成功 ===")
