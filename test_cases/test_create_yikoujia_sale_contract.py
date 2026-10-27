'''
Author: 章豹
Date: 2026-10-20 14:24:08
LastEditors: Do not edit
LastEditTime: 2026-10-27 14:49:14
'''
# -*- coding: utf-8 -*-
import pytest
from playwright.sync_api import expect
from pages.login_page import LoginPage
from pages.approval_page import ApprovalPage
from pages.sale_distribution_page import SaleDistributionPage
from pages.receipt_claim_page import ReceiptClaimPage
from pages.sale_invoice_apply_page import SaleInvoiceApplyPage
from pages.make_invoice_approval_page import MakeInvoiceApprovalPage
from utils.save_screenshot import save_screenshot
from pages.create_contract_page import CreateContractPage
from utils.log_print import get_logger
from utils.wait_utils import wait_for_text_change


class TestSaleContract:
    """一口价销售合同测试"""
    contract_code = None  # 类属性，用于跨测试方法共享数据
    # @pytest.mark.skip(reason="暂不执行新增销售合同")
    @pytest.mark.run(order=1)
    def test_add_sale_contract(self, page, host):
        """
        新增一口价销售合同
        """
        get_logger().info("=== 开始执行：新增一口价销售合同 ===")
        login_page = LoginPage(page)
        login_page.login(host=host)

        create_contract_page = CreateContractPage(page)
        # 传入 transaction_type="一口价销售"，其余字段与采购合同一致
        create_contract_page.create_contract(transaction_type="一口价销售")

        # 保存后验证合同编号不为空
        locator = page.locator("[name='logicContractCode']")
        save_screenshot(page, "销售合同创建")
        expect(locator).not_to_have_value("")
        # Vue 双向绑定只更新 value 属性（property），get_attribute 拿不到，必须用 input_value
        TestSaleContract.contract_code = locator.input_value()
        get_logger().info(f"新建销售合同号：{TestSaleContract.contract_code}")
        save_screenshot(page, "create_sale_contract.png")

    # @pytest.mark.skip(reason="暂不执行审批，需手动确认审批流程")
    @pytest.mark.run(order=2)
    def test_sale_contract_approval(self, page, host):
        """
        一口价销售合同-审批（可选执行）
        """
        get_logger().info("=== 开始执行：一口价销售合同审批 ===")
        login_page = LoginPage(page)
        login_page.login(host=host)
        approval_page = ApprovalPage(page)
        contract_code = TestSaleContract.contract_code
        approval_page.approval_process("补录", contract_code)
        # 查询合同详情获取最新状态
        approval_page.get_contract_details(contract_code)
        # 使用轮询等待检测文本变化
        container = page.locator("h3")
        approval_result = wait_for_text_change(
            container,
            "审核通过",
            timeout=30000,
            interval=500
        )
        save_screenshot(page, "销售合同审批结果")
        assert approval_result, f"审批失败，合同号: {contract_code}，未检测到'审核通过'文本"

    # @pytest.mark.skip(reason="暂不执行收款认领")
    @pytest.mark.run(order=3)
    def test_receipt_claim(self, page, host):
        """
        收款认领：审批通过后，对一口价销售合同执行收款认领
        """
        get_logger().info("=== 开始执行：收款认领 ===")
        login_page = LoginPage(page)
        login_page.login(host=host)

        contract_code = TestSaleContract.contract_code
        receipt_claim_page = ReceiptClaimPage(page)
        result = receipt_claim_page.execute_receipt_claim(contract_code)

        assert result is True, "收款认领执行失败"
        get_logger().info("=== 收款认领执行成功 ===")

    # @pytest.mark.skip(reason="暂不执行销售配货")
    @pytest.mark.run(order=4)
    def test_sale_distribution(self, page, host):
        """
        销售配货：审批通过后，对一口价销售合同执行销售配货
        """
        get_logger().info("=== 开始执行：销售配货 ===")
        login_page = LoginPage(page)
        login_page.login(host=host)

        contract_code = TestSaleContract.contract_code
        sale_distribution_page = SaleDistributionPage(page)
        result = sale_distribution_page.execute_sale_distribution(contract_code)

        assert result is True, "销售配货执行失败"
        get_logger().info("=== 销售配货执行成功 ===")

    # @pytest.mark.skip(reason="暂不执行销售申请开票")
    @pytest.mark.run(order=5)
    def test_sale_invoice_apply(self, page, host):
        """
        销售申请开票：销售配货后，对一口价销售合同执行销售申请开票
        """
        get_logger().info("=== 开始执行：销售申请开票 ===")
        login_page = LoginPage(page)
        login_page.login(host=host)

        contract_code = TestSaleContract.contract_code
        invoice_apply_page = SaleInvoiceApplyPage(page)
        result = invoice_apply_page.execute_full_apply(contract_code)

        assert result is True, "销售申请开票执行失败"
        get_logger().info("=== 销售申请开票执行成功 ===")

    # @pytest.mark.skip(reason="暂不执行开票指令审批")
    @pytest.mark.run(order=6)
    def test_make_invoice_approval(self, page, host):
        """
        开票指令审批：销售申请开票后，执行财务初审+匹配库存
        """
        get_logger().info("=== 开始执行：开票指令审批 ===")
        login_page = LoginPage(page)
        login_page.login(host=host)

        contract_code = TestSaleContract.contract_code
        approval_page = MakeInvoiceApprovalPage(page)
        result = approval_page.execute_full_approval(contract_code)

        assert result is True, "开票指令审批失败"
        get_logger().info("=== 开票指令审批执行成功 ===")
