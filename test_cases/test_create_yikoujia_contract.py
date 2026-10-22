'''
Author: 章豹
Date: 2026-09-18 09:27:42
LastEditors: Do not edit
LastEditTime: 2026-10-22 09:40:11
'''
# -*- coding: utf-8 -*-
import pytest
from playwright.sync_api import expect
from pages.login_page import LoginPage
from pages.approval_page import ApprovalPage
from pages.purchase_claim_page import PurchaseClaimPage
from utils.save_screenshot import save_screenshot
from pages.create_contract_page import CreateContractPage
from utils.log_print import get_logger
from utils.wait_utils import wait_for_text_change


class TestContract():
    contract_code = None  # 类属性，用于跨测试方法共享数据
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

    # @pytest.mark.run(order=3)
    def test_purchase_claim(self, page, host):
        """
        采购货物认领（衔接在审批之后，业务连贯）
        """
        get_logger().info("=== 开始执行：采购货物认领 ===")
        login_page = LoginPage(page)
        login_page.login(host=host)

        contract_code = TestContract.contract_code
        claim_page = PurchaseClaimPage(page)
        save_success = claim_page.execute_purchase_claim(contract_code='20261021-BDFZ-SFNSB002')

        save_screenshot(page, "采购货物认领完成")
        get_logger().info("=== 采购货物认领执行完毕 ===")

        assert save_success, "采购货物认领保存失败，未检测到成功提示"
