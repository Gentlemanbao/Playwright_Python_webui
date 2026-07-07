# -*- coding: utf-8 -*-
"""
@Time ： 2026/7/6 17:30
@Auth ： 章豹
@File ：save_screenshot.py
@IDE ：PyCharm
@LastEditTime ： 2026/7/6 17:30
"""

import allure
import datetime
import os


def save_screenshot(page, step_name=""):
    """
    保存测试截图
    :param page: Playwright page 对象
    :param step_name: 步骤名称，用于区分不同步骤的截图
    :return:
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    step_suffix = f"_{step_name}" if step_name else ""
    screenshot_path = f"picture/screenshots/failure_{timestamp}{step_suffix}.png"
    os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
    page.screenshot(path=screenshot_path, full_page=True)
    allure.attach.file(
        screenshot_path,
        name=f"截图_{step_name}" if step_name else "截图",
        attachment_type=allure.attachment_type.PNG
    )
    print(f"\n***截图已保存至: {screenshot_path} ***")