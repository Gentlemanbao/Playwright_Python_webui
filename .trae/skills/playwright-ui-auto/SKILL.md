---
name: "playwright-ui-auto"
description: "生成符合项目规范的Playwright UI自动化测试脚本。当用户需要创建新的页面对象或测试用例时调用此Skill。"
---

# Playwright UI 自动化测试脚本生成器

本Skill用于根据项目规范自动生成生产级可跑的UI自动化测试脚本，包括 Page Object 类和对应的测试用例。

## 1. 项目结构

```
ui_auto_project/
├── config/                     # 配置文件目录
│   ├── run_env.yml            # 执行环境配置
│   └── qx_environment.yml     # 系统环境地址配置
├── pages/                     # Page Object 页面对象目录
│   ├── login_page.py          # 登录页面
│   ├── create_contract_page.py# 合同创建页面
│   ├── goods_transfer_in_page.py # 入库指令页面
│   ├── public_operation.py    # 公共操作方法
│   └── __init__.py
├── test_cases/                # 测试用例目录
│   ├── test_login.py          # 登录测试用例
│   ├── test_create_yikoujia_contract.py # 合同创建测试用例
│   ├── test_goods_transfer_In.py # 入库指令测试用例
│   └── __init__.py
├── utils/                     # 工具类目录
│   ├── log_print.py           # 日志打印工具
│   ├── save_screenshot.py     # 截图工具
│   ├── encrypt.py             # 加密解密工具
│   ├── read_yaml.py           # YAML配置读取
│   ├── sql_service.py         # 数据库服务
│   └── public_operation.py    # 公共操作方法
├── sql_queries/               # SQL查询文件目录
├── conftest.py                # pytest配置与fixture
├── main.py                    # 主运行入口
├── pytest.ini                 # pytest配置文件
├── requirements.txt           # 依赖包清单
└── .trae/skills/              # Skill定义目录
```

## 2. Page Object 编写规范

### 2.1 文件头部注释

```python
# -*- coding: utf-8 -*-
"""
@Time ： 当前时间
@Auth ： 章豹
@File ：文件名.py
@IDE ：PyCharm
@LastEditTime ： 当前时间
"""
```

### 2.2 类结构模板

```python
# -*- coding: utf-8 -*-
"""
@Time ： YYYY/MM/DD HH:MM
@Auth ： 章豹
@File ：page_name.py
@IDE ：PyCharm
@LastEditTime ： YYYY/MM/DD HH:MM
"""

import time
from utils.log_print import get_logger
from utils.save_screenshot import save_screenshot

logger = get_logger()

class PageNamePage:
    """
    页面操作类
    """
    
    def __init__(self, page):
        self.page = page
        # 菜单元素
        self.menu_element = page.locator("text=菜单名称")
        # 输入框元素
        self.input_field = page.locator("[id='fieldId']")
        # 下拉框元素
        self.select_field = page.locator("xpath=//input[@id='selectId']")
        # 按钮元素
        self.submit_button = page.locator("text=提交")
    
    def navigate_to_page(self):
        """导航到目标页面"""
        self.menu_element.click()
    
    def fill_form(self, **kwargs):
        """填写表单"""
        # 使用 repetitive_operation 处理下拉框选择
        from pages.public_operation import repetitive_operation
        repetitive_operation(self.page, self.select_field, kwargs.get('value', '默认值'))
        self.input_field.fill(kwargs.get('input_text', ''))
    
    def submit_form(self):
        """提交表单"""
        save_screenshot(self.page, "提交前")
        self.submit_button.click()
        save_screenshot(self.page, "提交后")
```

### 2.3 元素定位规范

**优先使用以下定位方式（按优先级排序）：**

1. **ID 选择器**（最稳定）
   ```python
   self.username = page.locator("[id='username']")
   ```

2. **文本内容定位**（适合按钮、菜单）
   ```python
   self.login_btn = page.locator("text=登 录")
   ```

3. **XPath 定位**（适合复杂结构）
   ```python
   self.select_field = page.locator("xpath=//input[@id='fieldId']")
   ```

4. **语义化定位**（推荐用于角色组件）
   ```python
   self.combobox = page.get_by_role("combobox")
   ```

### 2.4 公共操作方法

#### repetitive_operation() - 下拉框/选择框操作

适用于 Ant Design Select 组件的选择操作：

```python
from pages.public_operation import repetitive_operation

# 普通选择
repetitive_operation(self.page, self.select_field, "选项文本")

# 点击后选择（需要先点击打开下拉框的场景）
repetitive_operation(self.page, self.select_field, "选项文本", is_click=True)
```

#### fill_cell() - 表格单元格填充

适用于表格中不同类型控件的填充：

```python
from pages.public_operation import fill_cell

# 普通输入框
fill_cell(self.page, cell, "值", field_type='input')

# 下拉选择框
fill_cell(self.page, cell, "选项文本", field_type='combobox')

# 数字输入框
fill_cell(self.page, cell, "100", field_type='spinbutton')

# 日期选择器
fill_cell(self.page, cell, "2026-07-10", field_type='datepicker')
fill_cell(self.page, cell, "today", field_type='datepicker')  # 选择今天
```

#### get_row_cell_by_header() - 按表头定位单元格

```python
from pages.public_operation import get_row_cell_by_header

# 获取表格新增行
new_row = page.locator("table tbody tr:last-child")
# 按表头名称获取单元格
cell = get_row_cell_by_header(page, new_row, "列头名称")
```

### 2.5 截图规范

```python
from utils.save_screenshot import save_screenshot

# 普通截图
save_screenshot(page, "步骤描述")

# 在关键操作前后截图
save_screenshot(page, "操作前")
self.submit_button.click()
save_screenshot(page, "操作后")
```

## 3. 测试用例编写规范

### 3.1 文件命名规则

```
test_<功能模块名称>.py
示例：test_create_contract.py, test_goods_transfer.py
```

### 3.2 测试类结构模板

```python
# -*- coding: utf-8 -*-
"""
@Time ： YYYY/MM/DD HH:MM
@Auth ： 章豹
@File ：test_module.py
@IDE ：PyCharm
@LastEditTime ： YYYY/MM/DD HH:MM
"""

from playwright.sync_api import expect
from utils.save_screenshot import save_screenshot
from pages.login_page import LoginPage
from pages.module_page import ModulePage
import pytest


def test_module_function(page, host):
    """
    测试XXX功能
    :param page: 浏览器页面对象（由conftest.py的fixture提供）
    :param host: 执行环境（test/uat/dev）
    """
    # 1. 登录
    login_page = LoginPage(page)
    login_page.login(host=host)
    
    # 2. 创建页面对象
    module_page = ModulePage(page)
    
    # 3. 执行操作
    module_page.execute_action()
    
    # 4. 截图验证
    save_screenshot(page, "操作完成")
    
    # 5. 断言验证
    expect(page.locator("text=操作成功")).to_be_visible(timeout=5000)
```

### 3.3 测试用例编写原则

1. **每个测试用例只测试一个功能点**
2. **使用 `page` 和 `host` fixture**（由 conftest.py 提供）
3. **断言使用 playwright expect API**
   ```python
   # 推荐：使用 expect API（自动等待）
   expect(page.locator("text=成功")).to_be_visible(timeout=5000)
   
   # 可选：使用 locator 断言
   assert page.locator("text=成功").is_visible(), "操作未成功"
   ```

4. **关键步骤添加截图**
5. **添加中文注释说明测试意图**

### 3.4 可用的 pytest fixture

| Fixture | 作用域 | 说明 |
|---------|--------|------|
| `page` | function | 每次测试创建新的浏览器页面 |
| `host` | function | 执行环境（test/uat/dev） |
| `browser` | session | 整个会话共用的浏览器实例 |

## 4. 代码生成流程

当用户描述业务需求时，按以下流程生成代码：

### 4.1 需求分析

从用户描述中提取：
- **功能模块名称**：如"合同管理"、"入库指令"
- **操作步骤**：如"点击新增→填写表单→提交"
- **表单字段**：如"客户名称"、"品种"、"数量"
- **预期结果**：如"保存成功提示"、"列表中出现新记录"

### 4.2 生成 Page Object

1. 根据功能模块命名：`<module_name>_page.py`
2. 提取页面元素定位器（根据用户描述的UI元素）
3. 封装业务操作方法
4. 使用项目公共方法（repetitive_operation、fill_cell等）

### 4.3 生成测试用例

1. 命名为 `test_<module_name>.py`
2. 导入 LoginPage 和新创建的 Page Object
3. 编写测试步骤：登录→页面导航→操作→断言
4. 添加截图和日志

### 4.4 验证代码

生成代码后，确保：
- 符合项目代码规范
- 使用项目现有的公共方法和工具类
- 包含必要的断言和截图
- 文件命名和路径正确

## 5. 常见场景示例

### 5.1 新增功能场景

```python
# pages/new_feature_page.py
class NewFeaturePage:
    def __init__(self, page):
        self.page = page
        self.new_button = page.locator("text=新增")
        self.form_field = page.locator("[id='fieldId']")
        self.save_button = page.locator("text=保存")
    
    def create_new(self, value):
        self.new_button.click()
        self.form_field.fill(value)
        self.save_button.click()

# test_cases/test_new_feature.py
def test_create_new_feature(page, host):
    login_page = LoginPage(page)
    login_page.login(host=host)
    feature_page = NewFeaturePage(page)
    feature_page.create_new("测试值")
    expect(page.locator("text=保存成功")).to_be_visible(timeout=5000)
```

### 5.2 查询功能场景

```python
# pages/search_page.py
class SearchPage:
    def __init__(self, page):
        self.page = page
        self.search_input = page.locator("[placeholder='请输入关键词']")
        self.search_button = page.locator("text=搜索")
        self.result_list = page.locator("table tbody tr")
    
    def search(self, keyword):
        self.search_input.fill(keyword)
        self.search_button.click()
    
    def get_result_count(self):
        return self.result_list.count()

# test_cases/test_search.py
def test_search_feature(page, host):
    login_page = LoginPage(page)
    login_page.login(host=host)
    search_page = SearchPage(page)
    search_page.search("测试关键词")
    assert search_page.get_result_count() > 0, "搜索结果为空"
```

### 5.3 审批流程场景

```python
# pages/approval_page.py
class ApprovalPage:
    def __init__(self, page):
        self.page = page
        self.approve_button = page.locator("text=审批通过")
        self.reject_button = page.locator("text=驳回")
        self.remark_input = page.locator("[id='remark']")
    
    def approve(self, remark="同意"):
        self.remark_input.fill(remark)
        self.approve_button.click()
    
    def reject(self, remark="不同意"):
        self.remark_input.fill(remark)
        self.reject_button.click()

# test_cases/test_approval.py
def test_approve_flow(page, host):
    login_page = LoginPage(page)
    login_page.login(host=host)
    approval_page = ApprovalPage(page)
    approval_page.approve("审批通过")
    expect(page.locator("text=审批完成")).to_be_visible(timeout=5000)
```

## 6. 注意事项

1. **Ant Design 组件处理**：项目使用 Ant Design UI 框架，下拉框、日期选择器等组件有特殊的定位方式，优先使用 `public_operation.py` 中的公共方法

2. **环境配置**：测试时通过 `host` fixture 传递环境标识（test/uat/dev），不要硬编码环境地址

3. **登录处理**：所有测试用例都需要先登录，复用 `LoginPage` 类

4. **截图时机**：在关键步骤（如提交前、操作后）添加截图，便于问题定位

5. **错误处理**：使用 try-except 处理可能的异常，并在异常时截图

6. **代码复用**：相同的操作模式（如表单填写、表格操作）尽量复用公共方法

## 7. 生成代码 Checklist

生成代码后，智能体必须检查以下项目：

- [ ] 文件头部注释格式正确
- [ ] Page Object 类继承结构合理
- [ ] 使用项目公共方法处理控件操作
- [ ] 测试用例使用 `page` 和 `host` fixture
- [ ] 包含必要的断言
- [ ] 关键步骤添加截图
- [ ] 代码符合项目命名规范
- [ ] 无硬编码环境地址
- [ ] 导入语句完整且正确