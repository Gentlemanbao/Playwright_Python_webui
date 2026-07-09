"""
Author: 章豹
Description: 公共操作方法
Date: 2026/7/6 17:30
LastEditTime: 2026/7/6 17:30
"""
import time


def repetitive_operation(page, page_obj, input_text=None, is_click=False):
        """
        重复操作方法,点击元素,输入文本,按下Enter键
        :param page_obj: 页面元素对象
        :param input_text: 输入文本
        """
        if is_click:
            page_obj.click()
        page_obj.fill(input_text)
        page.keyboard.press('Enter')
        # time.sleep(1)