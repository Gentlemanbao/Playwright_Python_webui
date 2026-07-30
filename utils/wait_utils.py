# -*- coding: utf-8 -*-
"""
@Time ： 2026/7/29 14:50
@Auth ： 章豹
@File ：wait_utils.py
@IDE ：PyCharm
@LastEditTime ： 2026/7/29 14:50
"""

import time
from utils.log_print import get_logger

logger = get_logger()


def wait_for_text_change(locator, expected_text, timeout=10000, interval=300):
    """
    轮询等待元素文本变化（适用于元素存在但文本异步更新的场景）
    
    :param locator: Playwright locator 对象，如 page.locator("h3")
    :param expected_text: 期望出现的文本
    :param timeout: 超时时间（毫秒）
    :param interval: 轮询间隔（毫秒）
    :return: bool - 是否成功等待到目标文本
    """
    start_time = time.time()
    timeout_seconds = timeout / 1000
    interval_seconds = interval / 1000
    
    while time.time() - start_time < timeout_seconds:
        try:
            current_text = locator.inner_text()
            logger.debug(f"当前文本: {current_text}, 期望文本: {expected_text}")
            
            if expected_text in current_text:
                logger.info(f"文本更新成功！当前文本: {current_text}")
                return True
                
        except Exception as e:
            logger.warning(f"获取元素文本失败: {e}")
        
        time.sleep(interval_seconds)
    
    logger.error(f"等待超时！在 {timeout}ms 内未检测到文本变化")
    return False


def wait_for_text_to_appear(page, selector, expected_text, timeout=10000, interval=300):
    """
    轮询等待指定选择器的元素出现目标文本
    
    :param page: Playwright page 对象
    :param selector: CSS选择器或XPath
    :param expected_text: 期望出现的文本
    :param timeout: 超时时间（毫秒）
    :param interval: 轮询间隔（毫秒）
    :return: bool - 是否成功等待到目标文本
    """
    locator = page.locator(selector)
    return wait_for_text_change(locator, expected_text, timeout, interval)


def wait_for_element_state_change(page, selector, state="visible", timeout=10000, interval=300):
    """
    轮询等待元素状态变化
    
    :param page: Playwright page 对象
    :param selector: CSS选择器或XPath
    :param state: 期望状态 (visible/hidden/attached/detached)
    :param timeout: 超时时间（毫秒）
    :param interval: 轮询间隔（毫秒）
    :return: bool - 是否成功
    """
    locator = page.locator(selector)
    start_time = time.time()
    timeout_seconds = timeout / 1000
    interval_seconds = interval / 1000
    
    while time.time() - start_time < timeout_seconds:
        try:
            if state == "visible" and locator.is_visible():
                logger.info("元素变为可见状态")
                return True
            elif state == "hidden" and not locator.is_visible():
                logger.info("元素变为隐藏状态")
                return True
            elif state == "attached" and locator.count() > 0:
                logger.info("元素已附加到DOM")
                return True
        except Exception as e:
            logger.debug(f"检查元素状态时出错: {e}")
        
        time.sleep(interval_seconds)
    
    logger.error(f"等待元素状态变化超时！期望状态: {state}")
    return False


def wait_with_retry(func, max_retries=3, retry_interval=1, *args, **kwargs):
    """
    通用重试等待装饰器
    
    :param func: 需要执行的函数
    :param max_retries: 最大重试次数
    :param retry_interval: 重试间隔（秒）
    :param args: 函数的位置参数
    :param kwargs: 函数的关键字参数
    :return: 函数执行结果或None
    """
    for attempt in range(1, max_retries + 1):
        try:
            result = func(*args, **kwargs)
            if result:
                return result
            logger.warning(f"第 {attempt} 次尝试返回空结果，{retry_interval}秒后重试...")
        except Exception as e:
            logger.warning(f"第 {attempt} 次尝试出错: {e}，{retry_interval}秒后重试...")
        
        if attempt < max_retries:
            time.sleep(retry_interval)
    
    logger.error(f"函数执行失败，已重试 {max_retries} 次")
    return None