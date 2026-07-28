# -*- coding: utf-8 -*-
"""
@Time ： 2026/7/28 9:40
@Auth ： 章豹
@File ：user_page.py
@IDE ：PyCharm
@LastEditTime ： 2026/7/28 9:40
"""

import time
from utils.log_print import get_logger
from utils.save_screenshot import save_screenshot
from pages.public_operation import repetitive_operation

logger = get_logger()


class UserPage:
    """
    用户管理页面操作类
    权限管理 -> 用户
    """
    
    def __init__(self, page):
        self.page = page
        # 菜单导航元素
        self.permission_menu = page.locator("text=权限管理")
        self.user_tab = page.locator("xpath=//div[text()='用户']")
        # 操作按钮
        self.add_button = page.locator("[title='创建用户']")
        self.search_button = page.locator("text=查 询")
        self.reset_button = page.locator("text=重 置")
        # 新增用户弹窗 - 必填字段
        self.username_input = page.locator("xpath=//div/input[@id='userAccount']")
        self.password_input = page.locator("[id='password']")
        self.confirm_password_input = page.locator("[id='surePassWrod']")
        self.email_input = page.locator("[id='email']")
        self.organization_select = page.locator("[id='customerId']")
        # 新增用户弹窗 - 非必填字段
        self.name_input = page.locator("[id='name']")
        self.phone_input = page.locator("[id='telephone']")
        self.mobile_input = page.locator("[id='mobile']")
        self.wechat_input = page.locator("[id='wechat']")
        self.global_code_input = page.locator("[id='jdUserCode']")
        self.department_select = page.locator("xpath=//input[@id='departmentId']")
        # 状态和性别单选
        self.status_enabled = page.locator("xpath=//span[text()='启用']")
        self.status_disabled = page.locator("xpath=//span[text()='禁用']")
        self.gender_male = page.locator("xpath=//span[text()='男']")
        self.gender_female = page.locator("xpath=//span[text()='女']")
        # 确定/取消按钮
        self.confirm_button = page.locator("text=确 定")
        self.cancel_button = page.locator("text=取 消")
        # 列表操作
        self.user_table = page.locator("table")
    
    def navigate_to_user_management(self):
        """导航到用户管理页面"""
        self.permission_menu.click()
        self.user_tab.click()
        logger.info("已导航到用户管理页面")
    
    def open_add_user_dialog(self):
        """打开新增用户弹窗"""
        self.add_button.click()
        logger.info("已打开新增用户弹窗")
    
    def fill_required_fields(self, username, password, email, organization, department):
        """
        填写必填字段
        :param username: 用户名
        :param password: 密码
        :param email: 邮箱
        :param organization: 机构名称
        :param department: 部门名称
        """
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.confirm_password_input.fill(password)
        self.email_input.fill(email)
        repetitive_operation(self.page, self.organization_select.nth(1), organization, is_click=True)
        repetitive_operation(self.page, self.department_select.nth(1), department, is_click=True)
        logger.info(f"已填写必填字段: 用户名={username}, 邮箱={email}, 机构={organization}")
    
    def fill_optional_fields(self, name="", gender="male", phone="", 
                            mobile="", wechat="", global_code=""):
        """
        填写非必填字段
        :param name: 姓名
        :param gender: 性别 male/female
        :param phone: 座机
        :param mobile: 手机
        :param wechat: 微信号
        :param global_code: 全球人员编码
        :param department: 部门
        """
        if name:
            self.name_input.nth(1).fill(name)
        if gender == "male":
            self.gender_male.click()
        elif gender == "female":
            self.gender_female.click()
        if phone:
            self.phone_input.fill(phone)
        if mobile:
            self.mobile_input.fill(mobile)
        if wechat:
            self.wechat_input.fill(wechat)
        if global_code:
            self.global_code_input.fill(global_code)
        logger.info(f"已填写非必填字段: 姓名={name}, 性别={gender}")
    
    def set_status(self, status="enabled"):
        """
        设置用户状态
        :param status: enabled(启用)/disabled(禁用)
        """
        if status == "enabled":
            self.status_enabled.nth(1).click()
        else:
            self.status_disabled.nth(1).click()
        logger.info(f"已设置用户状态为: {status}")
    
    def confirm_add_user(self):
        """确认新增用户"""
        save_screenshot(self.page, "新增用户表单填写完成")
        self.confirm_button.click()
        logger.info("已点击确定按钮提交")
    
    def cancel_add_user(self):
        """取消新增用户"""
        self.cancel_button.click()
        logger.info("已取消新增用户")
    
    def create_user(self, username, password, email, organization,
                   name="", gender="male", phone="", mobile="",
                   wechat="", global_code="", department="", status="enabled"):
        """
        完整的创建用户流程
        :param username: 用户名
        :param password: 密码
        :param email: 邮箱
        :param organization: 机构
        :param name: 姓名（可选）
        :param gender: 性别（可选）
        :param phone: 座机（可选）
        :param mobile: 手机（可选）
        :param wechat: 微信号（可选）
        :param global_code: 全球人员编码（可选）
        :param department: 部门（可选）
        :param status: 状态（启用/禁用）
        """
        self.navigate_to_user_management()
        self.open_add_user_dialog()
        self.fill_required_fields(username, password, email, organization,department)
        self.fill_optional_fields(name, gender, phone, mobile, wechat, global_code)
        self.set_status(status)
        self.confirm_add_user()
    
    def search_user(self, username="", user="", role="", department=""):
        """
        搜索用户
        :param username: 用户名
        :param user: 用户
        :param role: 角色
        :param department: 部门
        """
        if username:
            self.page.locator("[placeholder='请输入']").first.fill(username)
        self.search_button.click()
        logger.info(f"已搜索用户: 用户名={username}")
    
    def get_user_count(self):
        """获取当前列表用户数量"""
        return self.user_table.locator("tbody tr").count()