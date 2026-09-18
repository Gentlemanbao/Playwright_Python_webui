# -*- coding: utf-8 -*-
"""
@Time ： 2026/7/28 9:40
@Auth ： 章豹
@File ：test_create_user.py
@IDE ：PyCharm
@LastEditTime ： 2026/7/28 9:40
"""

import pytest
from playwright.sync_api import expect
from utils.save_screenshot import save_screenshot
from pages.login_page import LoginPage
from pages.user_page import UserPage


class TestCreateUser:
    """
    创建用户测试用例集
    """
    
    # ==================== 正向用例 ====================
    # @pytest.mark.skip(reason="登录测试用例跳过")
    def test_create_user_with_required_fields(self, page, host):
        """
        测试场景：仅填写必填字段创建用户
        前置条件：已登录系统，拥有用户管理权限
        测试步骤：
            1. 登录系统
            2. 导航到用户管理页面
            3. 点击新增按钮
            4. 填写必填字段（用户名、密码、确认密码、邮箱、机构）
            5. 点击确定提交
        预期结果：用户创建成功，显示成功提示
        """
        # 登录
        login_page = LoginPage(page)
        login_page.login(host=host)
        
        # 创建页面对象
        user_page = UserPage(page)
        
        # 准备测试数据
        test_username = "test_user_001"
        test_password = "Test@123456"
        test_email = "test_user_001@example.com"
        test_organization = "银河德睿资本管理有限公司"
        test_department = "德睿总部"
        
        # 执行创建用户操作
        user_page.navigate_to_user_management()
        save_screenshot(page, "进入用户管理页面")
        
        user_page.open_add_user_dialog()
        save_screenshot(page, "打开新增用户弹窗")
        
        user_page.fill_required_fields(
            username=test_username,
            password=test_password,
            email=test_email,
            organization=test_organization,
            department=test_department
        )
        save_screenshot(page, "填写必填字段完成")
        
        user_page.confirm_add_user()
        
        # 验证创建成功
        expect(page.locator(".el-message--success")).to_be_visible(timeout=5000)
        save_screenshot(page, "用户创建成功")
    
    @pytest.mark.skip(reason="登录测试用例跳过")
    def test_create_user_with_all_fields(self, page, host):
        """
        测试场景：填写所有字段创建用户
        前置条件：已登录系统，拥有用户管理权限
        测试步骤：
            1. 登录系统
            2. 导航到用户管理页面
            3. 点击新增按钮
            4. 填写所有字段
            5. 点击确定提交
        预期结果：用户创建成功，显示成功提示
        """
        # 登录
        login_page = LoginPage(page)
        login_page.login(host=host)
        
        # 创建页面对象
        user_page = UserPage(page)
        
        # 准备测试数据
        test_data = {
            "username": "test_user_full_001",
            "password": "Test@123456",
            "email": "test_user_full_001@example.com",
            "organization": "银河德睿资本管理有限公司",
            "name": "测试用户",
            "gender": "male",
            "phone": "021-12345678",
            "mobile": "13800138000",
            "wechat": "test_wechat",
            "global_code": "GLOBAL001",
            "department": "德睿总部",
            "status": "enabled"
        }
        
        # 执行创建用户操作
        user_page.navigate_to_user_management()
        save_screenshot(page, "进入用户管理页面")
        
        user_page.create_user(**test_data)
        
        # 验证创建成功
        expect(page.locator(".el-message--success")).to_be_visible(timeout=5000)
        save_screenshot(page, "用户创建成功")

    @pytest.mark.skip(reason="登录测试用例跳过")
    def test_create_user_with_disabled_status(self, page, host):
        """
        测试场景：创建禁用状态的用户
        前置条件：已登录系统，拥有用户管理权限
        测试步骤：
            1. 登录系统
            2. 导航到用户管理页面
            3. 点击新增按钮
            4. 填写必填字段，状态设为禁用
            5. 点击确定提交
        预期结果：用户创建成功，状态为禁用
        """
        # 登录
        login_page = LoginPage(page)
        login_page.login(host=host)
        
        # 创建页面对象
        user_page = UserPage(page)
        
        # 执行创建用户操作
        user_page.create_user(
            username="test_user_disabled_001",
            password="Test@123456",
            email="test_user_disabled_001@example.com",
            organization="银河德睿资本管理有限公司",
            name="禁用用户",
            status="disabled"
        )
        
        # 验证创建成功
        expect(page.locator(".el-message--success")).to_be_visible(timeout=5000)
        save_screenshot(page, "禁用用户创建成功")
    
    # ==================== 异常用例 ====================
    @pytest.mark.skip(reason="登录测试用例跳过")
    def test_create_user_with_empty_username(self, page, host):
        """
        测试场景：用户名为空时创建用户
        前置条件：已登录系统
        测试步骤：
            1. 登录系统
            2. 打开新增用户弹窗
            3. 不填写用户名，填写其他必填字段
            4. 点击确定提交
        预期结果：提示用户名不能为空
        """
        # 登录
        login_page = LoginPage(page)
        login_page.login(host=host)
        
        # 创建页面对象
        user_page = UserPage(page)
        
        # 执行操作
        user_page.navigate_to_user_management()
        user_page.open_add_user_dialog()
        
        # 不填写用户名，直接提交
        user_page.password_input.fill("Test@123456")
        user_page.confirm_password_input.fill("Test@123456")
        user_page.email_input.fill("test@example.com")
        
        save_screenshot(page, "用户名为空")
        user_page.confirm_button.click()
        
        # 验证错误提示
        expect(page.locator("text=请输入用户名")).to_be_visible(timeout=5000)
        save_screenshot(page, "显示用户名必填提示")
    
    @pytest.mark.skip(reason="登录测试用例跳过")
    def test_cancel_create_user(self, page, host):
        """
        测试场景：取消创建用户
        前置条件：已登录系统
        测试步骤：
            1. 登录系统
            2. 打开新增用户弹窗
            3. 填写部分字段
            4. 点击取消按钮
        预期结果：弹窗关闭，不创建用户
        """
        # 登录
        login_page = LoginPage(page)
        login_page.login(host=host)
        
        # 创建页面对象
        user_page = UserPage(page)
        
        # 执行操作
        user_page.navigate_to_user_management()
        user_page.open_add_user_dialog()
        
        # 填写部分字段
        user_page.username_input.fill("test_cancel_user")
        save_screenshot(page, "填写部分字段")
        
        # 点击取消
        user_page.cancel_button.click()
        
        # 验证弹窗已关闭
        expect(page.locator("text=确定")).not_to_be_visible()
        save_screenshot(page, "取消创建用户")