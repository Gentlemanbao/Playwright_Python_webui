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

logger = get_logger()


class UserPage:
    """
    用户管理页面操作类
    权限管理 -> 用户
    """
    
    def __init__(self, page):
        self.page = page
        # 菜单导航元素 (Vue Vben Admin)
        self.permission_menu = page.locator(".vben-menu-item__content:has-text('权限管理')")
        self.user_tab = page.locator(".el-tabs__item:has-text('用户')")
        # 操作按钮
        self.add_button = page.locator("button:has-text('创建用户')")
        self.search_button = page.locator("button:has-text('搜索')")
        self.reset_button = page.locator("button:has-text('重置')")
        # 新增用户弹窗容器 (Vue Vben Admin z-popup)
        self.dialog = page.locator(".z-popup")
        # 弹窗内表单字段 - 限定在弹窗内避免和表格同名冲突
        self.username_input = self.dialog.locator("[name='userAccount']")
        self.password_input = self.dialog.locator("[name='password']")
        self.confirm_password_input = self.dialog.locator("[name='surePassWrod']")
        self.email_input = self.dialog.locator("[name='email']")
        # select 字段：定位父级 el-select 组件
        self.customer_select = self.page.locator("[name='customerId']")
        self.department_select = self.page.locator("[name='departmentId']")
        self.name_input = self.dialog.locator("[name='name']")
        self.phone_input = self.dialog.locator("[name='telephone']")
        self.mobile_input = self.dialog.locator("[name='mobile']")
        self.wechat_input = self.dialog.locator("[name='wechat']")
        self.global_code_input = self.dialog.locator("[name='jdUserCode']")
        # 状态和性别单选
        self.status_enabled = self.dialog.locator("label:has-text('启用')")
        self.status_disabled = self.dialog.locator("label:has-text('禁用')")
        self.gender_male = self.dialog.locator("label:has-text('男')")
        self.gender_female = self.dialog.locator("label:has-text('女')")
        # 弹窗内确定/取消按钮
        self.confirm_button = self.dialog.locator("button:has-text('确认')")
        self.cancel_button = self.dialog.locator("button:has-text('取消')")
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
        # select 类字段：点击 el-select 父级 + fill + Enter
        # repetitive_operation(self.page, self.customer_select.nth(1), organization, is_click=True)
        self.customer_select.nth(1).click()
        self.customer_select.nth(1).fill(organization)
        self.page.keyboard.press("ArrowDown")
        self.page.keyboard.press("Enter")
        time.sleep(1)
        self.department_select.nth(1).click()
        self.department_select.nth(1).fill(department)
        time.sleep(1)
        self.page.keyboard.press("ArrowDown")
        self.page.keyboard.press("Enter")
        logger.info(f"已填写必填字段: 用户名={username}, 邮箱={email}, 机构={organization}, 部门={department}")
    
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
            self.name_input.fill(name)
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
        # 备用方案：使用 label 文本点击 radio
        # self.page.locator(f"label:has-text('{'启用' if status == 'enabled' else '禁用'}')").nth(1).click()
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