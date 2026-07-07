# UI自动化测试培训文档

## 目录

1. [环境搭建](#1-环境搭建)
2. [依赖包安装](#2-依赖包安装)
3. [框架介绍](#3-框架介绍)
4. [代码写法](#4-代码写法)
5. [Playwright基本操作](#5-playwright基本操作)
6. [用例扩展](#6-用例扩展)
7. [报告生成](#7-报告生成)
8. [常见问题](#8-常见问题)

---

## 1. 环境搭建

### 1.1 前置条件

- **操作系统**: Windows 10/11
- **Python版本**: 3.11.x
- **IDE**: PyCharm Community Edition

### 1.2 安装步骤

1. **安装Python 3.11**
   - 下载地址: https://www.python.org/downloads/release/python-3119/
   - 安装时勾选 "Add Python to PATH"

2. **安装PyCharm**
   - 下载地址: https://www.jetbrains.com/pycharm/download/
   - 选择 Community 版本

3. **安装Allure**
   - 下载地址: https://github.com/allure-framework/allure2/releases
   - 选择 `allure-2.30.0.zip` (或最新版本)
   - 解压到 `C:\allure-2.30.0`
   - 将 `C:\allure-2.30.0\bin` 添加到系统环境变量 PATH

4. **验证安装**
   ```bash
   python --version    # 输出: Python 3.11.9
   allure --version    # 输出: 2.30.0
   ```

---

## 2. 依赖包安装

### 2.1 安装命令

打开命令行，进入项目目录：

```bash
cd D:\期现项目资料\ui_auto_project
```

安装所有依赖包：

```bash
pip install pytest==7.4.4
pip install playwright==1.45.0
pip install allure-pytest==2.13.0
pip install pytest-html==4.1.1
pip install pytest-xdist==3.8.0
pip install pytest-rerunfailures==11.1.2
pip install cryptography==43.0.0
pip install pyyaml==6.0.1
```

### 2.2 安装浏览器驱动

```bash
playwright install chromium
```

### 2.3 依赖包说明

| 包名 | 版本 | 用途 |
|------|------|------|
| pytest | 7.4.4 | 测试框架 |
| playwright | 1.45.0 | UI自动化测试工具 |
| allure-pytest | 2.13.0 | 生成Allure测试报告 |
| pytest-html | 4.1.1 | 生成HTML测试报告 |
| pytest-xdist | 3.8.0 | 并行执行测试 |
| pytest-rerunfailures | 11.1.2 | 失败重跑 |
| cryptography | 43.0.0 | 加密解密 |
| pyyaml | 6.0.1 | 读取配置文件 |

---

## 3. 框架介绍

### 3.1 项目结构

```
ui_auto_project/
├── .idea/                 # PyCharm项目配置
├── config/                # 配置文件目录
│   ├── mysql_data.yml     # MySQL配置
│   ├── qx_environment.yml # 环境配置(用户名/密码/环境地址)
│   └── run_env.yml        # 运行环境配置
├── logs/                  # 日志文件
├── pages/                 # Page Object目录
│   ├── __init__.py
│   ├── login_page.py      # 登录页面封装
│   └── goods_transfer_in_page.py  # 入库指令页面封装
├── picture/               # 截图目录
│   └── screenshots/       # 测试截图
├── sql_queries/           # SQL查询语句
├── temp/                  # Allure原始数据
├── test_cases/            # 测试用例目录
│   ├── __init__.py
│   ├── test_login.py      # 登录测试用例
│   └── test_goods_transfer_In.py  # 入库指令测试用例
├── utils/                 # 工具类目录
│   ├── __init__.py
│   ├── case_pretask.py    # 测试前清理
│   ├── encrypt.py         # 加密解密工具
│   ├── log_print.py       # 日志工具
│   ├── read_yaml.py       # YAML读取工具
│   ├── remove_file.py     # 文件删除工具
│   ├── save_screenshot.py # 截图工具
│   └── sql_service.py     # SQL服务工具
├── conftest.py            # Pytest配置文件
├── main.py                # 主运行入口
└── pytest.ini             # Pytest配置
```

### 3.2 核心组件说明

| 组件 | 文件 | 作用 |
|------|------|------|
| **配置管理** | `config/qx_environment.yml` | 管理不同环境的URL、用户名、密码 |
| **日志系统** | `utils/log_print.py` | 记录运行日志到文件和控制台 |
| **截图工具** | `utils/save_screenshot.py` | 保存截图并附加到Allure报告 |
| **Page Object** | `pages/*.py` | 封装页面元素和操作方法 |
| **测试夹具** | `conftest.py` | 管理浏览器和页面的生命周期 |
| **运行入口** | `main.py` | 一键执行测试并生成报告 |

### 3.3 执行流程

```
main.py 
    ↓
pre_task() 清理历史报告和截图
    ↓
pytest 执行测试用例
    ↓
conftest.py 启动浏览器
    ↓
pages/*.py 页面操作
    ↓
utils/save_screenshot.py 截图
    ↓
allure generate 生成报告
```

---

## 4. 代码写法

### 4.1 Page Object 编写规范

#### 4.1.1 页面类结构

```python
# -*- coding: utf-8 -*-
"""
@Time ： 2026/7/7 10:00
@Auth ： 章豹
@File ：example_page.py
@IDE ：PyCharm
@LastEditTime ： 2026/7/7 10:00
"""

from utils.save_screenshot import save_screenshot

class ExamplePage:
    def __init__(self, page):
        self.page = page  # 必须保存page对象
        # 元素定位器，使用有意义的变量名
        self.username_input = page.locator("[id='username']")
        self.submit_button = page.locator("[title='提交']")
    
    def fill_form(self, username):
        """填写表单"""
        self.username_input.fill(username)
        save_screenshot(self.page, "填写表单")
        self.submit_button.click()
```

#### 4.1.2 元素定位优先级

| 优先级 | 方法 | 示例 | 说明 |
|--------|------|------|------|
| 1 | `page.get_by_role()` | `page.get_by_role("button", name="登录")` | 推荐，语义化定位 |
| 2 | `page.get_by_text()` | `page.get_by_text("登录", exact=True)` | 精确文本匹配 |
| 3 | `page.locator("[id='xxx']")` | `page.locator("[id='username']")` | ID定位，稳定 |
| 4 | `page.locator("[title='xxx']")` | `page.locator("[title='新增']")` | Title属性 |
| 5 | `page.locator("xpath=//...")` | `page.locator("xpath=//span[text()='确定']")` | XPath，慎用 |

#### 4.1.3 常用元素定位方法详解

Playwright 提供了多种定位元素的方式，推荐使用 `locator` 方法（自动等待元素可见，无需手动处理延迟）。

| 方法 | 示例 | 说明 |
|------|------|------|
| CSS 选择器 | `page.locator("#username")` | 通过 ID 定位 |
| CSS 选择器 | `page.locator(".btn-submit")` | 通过类名定位 |
| CSS 选择器 | `page.locator("input[type='text']")` | 通过标签和属性定位 |
| CSS 选择器 | `page.locator("[data-test='submit']")` | 通过自定义属性定位 |
| XPath 表达式 | `page.locator("//input[@name='password']")` | 通过 XPath 定位 |
| XPath 表达式 | `page.locator("//span[text()='登录']")` | 通过文本内容定位 |
| XPath 表达式 | `page.locator("//div[@class='form']//input")` | 层级定位 |
| 文本内容 | `page.locator("text=登录")` | 匹配元素文本（模糊匹配） |
| 文本内容 | `page.locator("text='登 录'")` | 精确匹配（带引号） |
| 占位符 | `page.locator("placeholder=请输入密码")` | 匹配输入框占位符 |
| 标签文本 | `page.locator("label:has-text('用户名')")` | 组合定位（标签包含文本） |
| Title 属性 | `page.locator("[title='新增']")` | 通过 title 属性定位 |
| 角色定位 | `page.get_by_role("button", name="提交")` | 语义化定位，推荐 |
| 占位符定位 | `page.get_by_placeholder("请输入用户名")` | 通过占位符定位 |

#### 4.1.4 元素定位最佳实践

1. **优先使用语义化定位**：
   ```python
   # 推荐：语义化，不易受UI变化影响
   page.get_by_role("button", name="登 录")
   ```

2. **使用稳定的属性**：
   ```python
   # 推荐：使用ID或自定义属性
   page.locator("[id='username']")
   page.locator("[data-test='submit-btn']")
   ```

3. **避免使用不稳定的定位器**：
   ```python
   # 不推荐：依赖页面结构，容易失效
   page.locator("xpath=//div[2]/div[3]/button")
   ```

4. **处理动态内容**：
   ```python
   # 使用部分文本匹配
   page.locator("text*=操作成功")  # 包含"操作成功"的文本
   page.locator("text^=欢迎")       # 以"欢迎"开头的文本
   ```

5. **等待元素可见**：
   ```python
   # Playwright 会自动等待元素可操作
   locator = page.locator("[id='submit']")
   locator.click()  # 自动等待元素可见并可点击
   ```

### 4.2 测试用例编写规范

#### 4.2.1 测试用例结构

```python
# -*- coding: utf-8 -*-
"""
@Time ： 2026/7/7 10:00
@Auth ： 章豹
@File ：test_example.py
@IDE ：PyCharm
@LastEditTime ： 2026/7/7 10:00
"""

from playwright.sync_api import expect
from playwright.sync_api._generated import Page
from pages.login_page import LoginPage
from pages.example_page import ExamplePage
from utils.save_screenshot import save_screenshot

def test_example_function(page: Page):
    # 1. 登录
    login_page = LoginPage(page)
    login_page.login(host="test")  # host可选: test/uat/dev
    
    # 2. 业务操作
    example_page = ExamplePage(page)
    example_page.fill_form("test_user")
    
    # 3. 断言验证
    expect(page.locator("text=操作成功")).to_be_visible(timeout=3000)
    
    # 4. 截图记录
    save_screenshot(page, "测试完成")
```

#### 4.2.2 断言方式

**推荐使用 `expect` API**（自动等待元素）：

```python
# 验证元素可见
expect(page.locator("text=操作成功")).to_be_visible(timeout=5000)

# 验证元素包含文本
expect(page.locator("[id='message']")).to_have_text("操作成功")

# 验证元素计数
expect(page.locator("tr")).to_have_count(10)

# 验证页面URL
expect(page).to_have_url("http://192.168.10.137/biz/index")
```

**避免使用裸断言**（不会等待）：

```python
# 不推荐
assert page.locator("text=操作成功").is_visible()  # 可能因为页面未加载完成而失败

# 如果必须使用，先等待
locator = page.locator("text=操作成功")
locator.wait_for(timeout=5000)
assert locator.is_visible(), "元素不可见"
```

### 4.3 配置文件编写

#### 4.3.1 环境配置 (`config/qx_environment.yml`)

```yaml
# 环境地址
test: 192.168.10.137
uat: 192.168.10.138
dev: 192.168.10.139

# 登录信息
username: yunwei2
password: encrypted_password
key: encryption_key
```

#### 4.3.2 Pytest配置 (`pytest.ini`)

```ini
[pytest]
testpaths = test_cases
addopts = 
    -vs                    # 详细输出
    --capture=no           # 不捕获标准输出
    --alluredir=./temp     # Allure报告目录
python_files = test*       # 测试文件命名规则
python_classes = Test*     # 测试类命名规则
python_functions = test*   # 测试函数命名规则
markers =
    smoke: 冒烟测试
    run: 执行顺序
log_cli = true             # 控制台输出日志
log_cli_level = INFO       # 日志级别
```

---

## 5. Playwright基本操作

### 5.1 页面操作

```python
# 打开URL
page.goto("http://192.168.10.137/user/login/")

# 等待页面加载
page.wait_for_load_state("networkidle")  # 等待网络空闲
page.wait_for_load_state("load")         # 等待页面加载完成

# 获取当前URL
current_url = page.url

# 后退/前进
page.go_back()
page.go_forward()

# 刷新页面
page.reload()
```

### 5.2 元素操作

```python
# 定位元素
locator = page.locator("[id='username']")

# 输入文本
locator.fill("test_user")

# 点击
locator.click()

# 清空输入框
locator.clear()

# 获取文本
text = locator.inner_text()

# 获取属性值
value = locator.get_attribute("value")

# 键盘操作
page.keyboard.press('Enter')           # 按回车
page.keyboard.press('ArrowDown')       # 按向下箭头
page.keyboard.press('Backspace')       # 按删除键
page.keyboard.type("hello", delay=100) # 输入文本，每个字符间隔100ms

# 鼠标操作
locator.hover()                        # 悬停
locator.dblclick()                     # 双击
locator.click(button="right")          # 右键点击
```

### 5.3 等待机制

```python
# 等待元素出现（默认超时30000ms）
locator.wait_for(timeout=5000)

# 等待元素可见
expect(locator).to_be_visible(timeout=5000)

# 等待元素隐藏
expect(locator).to_be_hidden(timeout=5000)

# 等待响应
with page.expect_response("**/api/login") as response_info:
    login_button.click()
response = response_info.value
```

### 5.4 截图操作

```python
# 截取整个页面
page.screenshot(path="screenshot.png", full_page=True)

# 截取指定元素
locator.screenshot(path="element.png")
```

---

## 6. 用例扩展

### 6.1 添加新的Page Object

1. 在 `pages/` 目录下创建新文件 `new_page.py`
2. 编写页面类，继承Page Object模式
3. 在测试用例中导入并使用

示例：

```python
# pages/new_page.py
class NewPage:
    def __init__(self, page):
        self.page = page
        self.menu_item = page.locator("[title='新菜单']")
    
    def navigate(self):
        self.menu_item.click()
```

### 6.2 添加新的测试用例

1. 在 `test_cases/` 目录下创建新文件 `test_new_feature.py`
2. 编写测试函数，使用 `def test_xxx(page):` 格式
3. 通过 `main.py` 或直接运行 pytest 执行

示例：

```python
# test_cases/test_new_feature.py
def test_new_feature(page):
    login_page = LoginPage(page)
    login_page.login(host="test")
    
    new_page = NewPage(page)
    new_page.navigate()
    
    expect(page.locator("text=新功能页面")).to_be_visible(timeout=3000)
```

### 6.3 运行指定测试

```bash
# 运行单个测试文件
pytest test_cases/test_login.py -v

# 运行单个测试函数
pytest test_cases/test_login.py::test_login_with_po -v

# 运行多个测试文件
pytest test_cases/test_login.py test_cases/test_goods_transfer_In.py -v

# 使用markers运行
pytest -m smoke -v

# 并行运行（需要pytest-xdist）
pytest -n=3 -v
```

### 6.4 调试技巧

```python
# 在代码中添加断点
import pdb; pdb.set_trace()

# 使用slow_mo减速观察（在conftest.py中设置）
browser = playwright.chromium.launch(headless=False, slow_mo=500)

# 打印页面内容
print(page.content())

# 截图调试
page.screenshot(path="debug.png")
```

---

## 7. 报告生成

### 7.1 生成Allure报告

**方式一：通过main.py运行（推荐）**

```bash
python main.py
```

**方式二：手动生成**

```bash
# 运行测试，生成原始数据
pytest --alluredir ./temp

# 生成HTML报告
allure generate ./temp -o .report --clean

# 启动本地服务查看报告
allure serve ./temp
```

### 7.2 报告结构

```
.report/
├── index.html        # 报告入口
├── data/             # 测试数据
│   ├── test-cases/   # 测试用例详情
│   └── attachments/  # 截图附件
├── plugins/          # 报告插件
└── widgets/          # 统计图表
```

### 7.3 查看报告

**方式一：使用allure serve（推荐）**

```bash
allure serve ./temp
```

会自动启动HTTP服务，浏览器打开查看。

**方式二：打开本地HTML**

```bash
# 启动HTTP服务器
cd .report
python -m http.server 8080
```

然后在浏览器访问 `http://localhost:8080`

> **注意**：不能直接双击打开 `index.html`，会因为浏览器安全策略无法加载数据。

### 7.4 报告内容说明

| 区域 | 内容 |
|------|------|
| **Overview** | 测试统计概览（通过/失败/跳过） |
| **Categories** | 失败分类 |
| **Suites** | 测试套件层级展示 |
| **Graphs** | 统计图表（执行时间、趋势等） |
| **Timeline** | 执行时间线 |
| **Behaviors** | 按功能模块分组 |

---

## 8. 常见问题

### 8.1 环境配置问题

**Q1: 运行时提示找不到页面元素**

A: 检查以下几点：
- 确认环境地址正确（`host`参数: test/uat/dev）
- 确认元素定位器正确
- 确认页面已加载完成（使用`wait_for_load_state`）

**Q2: 登录失败**

A: 检查 `config/qx_environment.yml` 中的用户名和密码是否正确。

### 8.2 测试执行问题

**Q3: 提示 `fixture 'page' not found`**

A: 在项目根目录运行pytest，不要在 `test_cases/` 子目录运行：
```bash
cd D:\期现项目资料\ui_auto_project
pytest test_cases/test_login.py -v
```

**Q4: 提示 `TypeError: 'module' object is not callable`**

A: 导入方式错误，确保导入的是函数而非模块：
```python
# 错误
from utils import save_screenshot  # 导入的是模块

# 正确
from utils.save_screenshot import save_screenshot  # 导入的是函数
```

**Q5: Allure报告为空**

A: 确认运行pytest时指定了 `--alluredir` 参数：
```bash
pytest --alluredir ./temp
```

### 8.3 代码编写问题

**Q6: `is_visible()` 返回False但页面上能看到元素**

A: `is_visible()` 不会等待元素出现，改用 `expect` API：
```python
expect(page.locator("text=元素文本")).to_be_visible(timeout=5000)
```

**Q7: Page Object中使用 `self.page` 报错**

A: 在 `__init__` 方法中忘记保存 `self.page`：
```python
def __init__(self, page):
    self.page = page  # 必须添加这行
    self.username_input = page.locator("[id='username']")
```

### 8.4 报告查看问题

**Q8: 报告页面一直显示loading**

A: 必须通过HTTP服务打开报告，不能直接双击HTML文件：
```bash
allure serve ./temp
```

**Q9: 截图未显示在报告中**

A: 检查 `save_screenshot.py` 中是否调用了 `allure.attach.file()`：
```python
allure.attach.file(
    screenshot_path,
    name="截图",
    attachment_type=allure.attachment_type.PNG
)
```

---

## 附录

### A. 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+Shift+F10` | 运行当前测试用例 |
| `Ctrl+D` | 复制当前行 |
| `Ctrl+Y` | 删除当前行 |
| `Ctrl+/` | 注释/取消注释 |
| `Alt+Enter` | 快速修复 |

### B. 常用命令

```bash
# 安装依赖
pip install xxx==version

# 升级依赖
pip install --upgrade xxx

# 查看已安装包
pip list

# 导出依赖清单
pip freeze > requirements.txt

# 安装依赖清单
pip install -r requirements.txt
```

### C. 编写规范

1. 文件头部统一使用项目模板生成
2. 函数和变量命名使用小写字母加下划线（snake_case）
3. 类名使用驼峰命名（CamelCase）
4. 每个函数添加文档字符串说明
5. 关键操作添加截图记录
6. 使用 `expect` API 进行断言
7. 避免使用 `time.sleep()`，改用 `wait_for()`

---

**文档版本**: v1.0  
**创建时间**: 2026/7/7  
**作者**: 章豹