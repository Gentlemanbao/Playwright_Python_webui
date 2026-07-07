# -*- coding: utf-8 -*-
"""
@Time ： 2026/7/6 17:30
@Auth ： 章豹
@File ：conftest.py
@IDE ：PyCharm
@LastEditTime ： 2026/7/6 17:30
"""
from typing import Any, Generator
from venv import logger
from pathlib import Path
import pytest
import os
from playwright.sync_api import Page, Browser, BrowserContext, sync_playwright
import datetime
from utils.read_yaml import ReadConfig

# 项目根目录
PROJECT_ROOT = Path(__file__).parent

@pytest.fixture(scope="session")
def browser() -> Generator[Browser, Any, None]:
    """
    会话级别的夹具，整个测试会话只启动一次浏览器。
    使用 yield 实现 teardown，测试全部结束后关闭浏览器。
    """
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False, args=[
        # '--disable-dev-shm-usage', # 克服Docker等环境下的资源限制问题
        # '--no-sandbox',
        # '--disable-gpu',
        '--slow_mo=500'
    ]) # slow_mo 让操作变慢，方便观察，启动Chromium浏览器，headless=False表示有界面，便于调试。正式运行可设为True。
    run_env_path = PROJECT_ROOT / "config" / "run_env.yml"
    red_env = ReadConfig(str(run_env_path))
    host = red_env.read_data("run")
    logger.info(f"获取执行环境: {host}")
    yield browser, host # 将浏览器实例提供给测试用例
    browser.close()
    playwright.stop()


# 在 conftest.py 中新增或修改 page 夹具
@pytest.fixture
def page(browser):
    browser_instance, _ = browser
    context = browser_instance.new_context(viewport={"width": 1920, "height": 1080})
    page = context.new_page()
    yield page
    context.close()

@pytest.fixture
def host(browser):
    _, host = browser  # 从 browser fixture 解包出 host
    return host

# 这个钩子函数用于在测试调用后存储结果
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    # 将结果存储到节点中，供 page 夹具访问
    setattr(item, "rep_" + rep.when, rep)
