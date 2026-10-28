'''
Author: 章豹
Date: 2026-10-27 16:54:09
LastEditors: Do not edit
LastEditTime: 2026-10-28 10:45:59
'''
# -*- coding: utf-8 -*-
"""
Author: 章豹
Date: 2026-10-27

仓单转入测试用例
"""
import pytest
from pages.login_page import LoginPage
from pages.receipt_transfer_in_page import ReceiptTransferInPage
from utils.log_print import get_logger


class TestReceiptTransferIn:
    """仓单转入测试"""
    instruction_no = None  # 类属性，用于跨测试方法共享数据

    # @pytest.mark.skip(reason="暂不执行仓单转入新增")
    @pytest.mark.run(order=1)
    def test_receipt_transfer_in_add(self, page, host):
        """
        仓单转入新增：货权运营→货权指令执行→仓单转入→新增→填写明细→确定→断言→提取指令编号
        """
        get_logger().info("=== 开始执行：仓单转入新增 ===")
        login_page = LoginPage(page)
        login_page.login(host=host)
        transfer_in_page = ReceiptTransferInPage(page)
        instruction_no = transfer_in_page.execute_full_add()
        assert instruction_no is not None and instruction_no != "", "指令编号获取失败"
        TestReceiptTransferIn.instruction_no = instruction_no
        get_logger().info(f"=== 仓单转入新增成功，指令编号: {instruction_no} ===")

    @pytest.mark.run(order=2)
    def test_receipt_transfer_in_approval(self, page, host):
        """
        仓单转入审批：货权运营→货权指令执行→仓单转入→搜索指令编号→货权管理部复核→审核通过→断言已完成
        """
        get_logger().info("=== 开始执行：仓单转入审批 ===")
        login_page = LoginPage(page)
        login_page.login(host=host)

        transfer_in_page = ReceiptTransferInPage(page)
        result = transfer_in_page.execute_full_approval('CDCR-202610-000008')

        assert result is True, "仓单转入审批执行失败"
        get_logger().info("=== 仓单转入审批执行成功 ===")
