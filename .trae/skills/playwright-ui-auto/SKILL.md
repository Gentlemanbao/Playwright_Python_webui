---
name: "playwright-ui-auto"
description: "生成符合项目规范的Playwright UI自动化测试脚本。当用户需要创建新的页面对象或测试用例时调用此Skill。"
---

# Playwright UI 自动化测试脚本生成器

本Skill用于根据项目规范自动生成生产级可跑的UI自动化测试脚本，包括 Page Object 类和对应的测试用例。

## 0. 被测系统与技术栈（先读这条，避免用错框架）

| 项 | 实际值 |
|---|---|
| 被测系统 | 银河德睿（Vue3 + **Element Plus** + **Vben Admin**，测试环境 `http://192.168.100.147/biz`） |
| 测试框架 | pytest + **Playwright sync API**（`headless=False`、`slow_mo=500`、viewport 1920x1080） |
| 运行解释器 | 系统 Python 3.11.9（`C:\Users\admin\AppData\Local\Programs\Python\Python311\python.exe`） |
| ⚠️ 注意 | **不是 Ant Design**。下拉是 Element Plus 的 `el-select`，菜单是 vben 的 `.vben-sub-menu / .vben-menu-item__content` |

## 1. 项目结构

```
ui_auto_project/
├── config/
│   ├── run_env.yml            # 执行环境标识（test/uat/dev）
│   ├── qx_environment.yml     # 各环境地址 + 登录账号(密文)/密钥
│   └── mysql_data.yml         # 数据库连接
├── pages/                     # Page Object 页面对象（★ 不要放 utils）
│   ├── login_page.py
│   ├── public_operation.py    # ★ 公共操作方法都在这里
│   ├── create_contract_page.py
│   ├── approval_page.py
│   ├── goods_transfer_in_page.py
│   ├── user_page.py
│   └── __init__.py
├── test_cases/
│   ├── test_login.py
│   ├── test_create_yikoujia_contract.py
│   ├── test_goods_transfer_In.py
│   ├── test_create_user.py
│   └── __init__.py
├── utils/                     # 工具类（只读复用，不要改）
│   ├── log_print.py           # get_logger()
│   ├── save_screenshot.py     # save_screenshot(page, "描述")
│   ├── encrypt.py             # decrypt()
│   ├── read_yaml.py           # ReadConfig
│   ├── wait_utils.py          # wait_for_text_change()
│   ├── sql_service.py         # 数据库查询
│   ├── case_pretask.py        # 用例前置数据准备
│   ├── remove_file.py / run_edit.py
├── sql_queries/               # 各用例的 SQL 文件
├── conftest.py                # browser / page / host fixture
├── main.py                    # 主运行入口
├── pytest.ini                 # testpaths 指向当前调试的用例（写新用例时建议挂上）
└── .trae/skills/              # Skill定义目录
```

## 2. 硬性要求：文件头部注释（必须遵守）

### ⚠️ 强制规则
**每次使用 Write 工具创建新文件时，必须在文件开头添加以下头部注释，缺一不可！**

### 2.1 头部注释模板

```python
# -*- coding: utf-8 -*-
"""
@Time ： {YYYY/M/D HH:MM}
@Auth ： 章豹
@File ：{文件名}
@IDE ：PyCharm
@LastEditTime ： {YYYY/M/D HH:MM}
"""
```

### 2.2 生成规则
- `@Time` / `@LastEditTime`：当前系统时间，格式 `YYYY/M/D HH:MM`
- `@Auth`：固定 `章豹`；`@IDE`：固定 `PyCharm`
- `@File`：实际文件名，如 `user_page.py`

### 2.3 ⚠️ 致命坑：绝对不要写 `FilePath` 并使用反斜杠

编辑器插件（koroFileHeader）曾自动生成：
```python
FilePath: \ui_auto_project\test_cases\test_create_yikoujia_contract.py
```
里面的 `\u` 会被 Python 当成 **unicode 转义**，导致**整个文件 SyntaxError、0 个用例被收集**（已踩过一次）。

- 若必须写 FilePath，**一律使用正斜杠**：`FilePath: ui_auto_project/test_cases/xxx.py`
- 或者干脆不写 FilePath 行。
- 新建/修改文件后，务必先 `python -m py_compile <文件>` 验证。

## 3. Page Object 类结构模板

```python
# -*- coding: utf-8 -*-
"""
@Time ： 2026/9/18 09:30
@Auth ： 章豹
@File ：xxx_page.py
@IDE ：PyCharm
@LastEditTime ： 2026/9/18 09:30
"""
import re
import time
from utils.log_print import get_logger
from utils.save_screenshot import save_screenshot
from pages.public_operation import select_dropdown_option, repetitive_operation

logger = get_logger()


def _ancestor_el_select(locator):
    """根据 name 属性定位 input，再向上找最外层 .el-select 组件（避免匹配到嵌套子 div）"""
    return locator.first.locator(
        "xpath=ancestor::div[contains(@class,'el-select') and not(contains(@class,'el-select__'))]"
    )


class XxxPage:
    """页面操作类"""

    def __init__(self, page):
        self.page = page
        # 菜单导航（vben）
        self.xxx_menu = page.locator(".vben-sub-menu:has-text('菜单名')")
        # 下拉框：统一用 _ancestor_el_select + [name='字段名']
        self.xxx_select = _ancestor_el_select(page.locator("[name='xxxField']"))
        # 普通输入框
        self.xxx_input = page.locator("[name='xxxField']")
        # 按钮：精确匹配，避免命中同名后缀按钮（如"保存" vs "本地保存"）
        self.save_button = page.locator("button").filter(has_text=re.compile(r"^\s*保存\s*$"))

    def fill_form(self, **kwargs):
        """填写表单"""
        select_dropdown_option(self.page, self.xxx_select, kwargs.get("value", "默认值"))
        self.xxx_input.fill(kwargs.get("input_text", ""))

    def submit_form(self):
        save_screenshot(self.page, "提交前")
        self.save_button.first.click()
        save_screenshot(self.page, "提交后")
```

### 3.1 元素定位规范（按优先级）

1. **`[name='字段名']`**（本项目表单字段几乎都带 name，最稳）
   - 下拉必须再套 `_ancestor_el_select()` 找到最外层 `.el-select`
2. **文本定位**（按钮/菜单）：`page.locator("button:has-text('搜索')")`
   - ⚠️ 同前缀按钮必须用 `filter(has_text=re.compile(r"^\s*XXX\s*$"))` 精确匹配
3. **placeholder**：`page.locator("[placeholder='请输入合约编号']")`
4. 表格 → 见 3.2 的 vxe-table 专用方法

### 3.2 公共操作方法（`pages/public_operation.py`）

#### select_dropdown_option(page, select_locator, text, timeout=8000) —— ★ 首选下拉选择

```python
from pages.public_operation import select_dropdown_option

select_dropdown_option(page, self.customer_select, "北大方正物产集团有限公司")
```

行为要点（已内置，无需在用例里重复处理）：
- 用 input 的 `aria-expanded` 判断**本组件**面板是否展开、`aria-controls` 精确拿到**本组件自己的**面板
- 可搜索组件先在组件内部 `.el-select__input` 输入关键词触发过滤
- 选中动作用 **JS click**（不触发 Playwright 自动滚动 → 页面不会跳动）
- 选中后校验展示文本，未生效自动重试 3 次
- 找不到时抛异常并打印面板全部选项，便于确认选项真实文本

#### repetitive_operation(page, page_obj, input_text, is_click=False) —— 兼容老写法

- 传入的是 **el-select 组件（div）** → 内部转调 `select_dropdown_option`
- 传入的是 **普通 input** → `click(force) → fill → ArrowDown → Enter`
- **日期输入框**用 `is_click=True`：`repetitive_operation(page, self.start_date, "2026-06-01", is_click=True)`

#### vxe-table 系列（货物明细表专用，★★ 重要）

货物明细表是 **vxe-table**（不是 el-table），三个特性决定了必须用专用方法：
1. 表头/数据行/固定列**分属不同的 `<table>`** → 禁止全局 `table tbody tr:last-child`
2. **点击单元格才激活编辑** → 点了才渲染出 `el-select` / `el-input-number`
3. **列虚拟渲染** → 46 列里只有可视区 ~9 列有 td，未渲染的列定位直接超时

```python
from pages.public_operation import get_vxe_table_by_header, vxe_fill_cell

# 每次填充前重新定位（表格会因联动重建，列 id 会变）
table = get_vxe_table_by_header(self.page)          # 按特征列头"未选仓库备注"定位表格
vxe_fill_cell(self.page, table, "仓库名", "上海象屿钢铁供应链有限公司（上海象屿钢铁宝山库）", field_type='combobox')
vxe_fill_cell(self.page, table, "件数", "100", field_type='spinbutton')
vxe_fill_cell(self.page, table, "生产日期", "2026-07-10", field_type='datepicker')
```

- 可用方法：`get_vxe_table_by_header` / `get_vxe_colid` / `get_vxe_data_row` / `vxe_scroll_to_column` / `vxe_fill_cell`
- **列头文本必须和页面上完全一致**，含 `*`（如 `品名*`、`总重量 *`、`点价成交价*`、`基差 *`、`升贴水 *`）；不确定就先 dump 表头
- 滚动容器是 `.vxe-table--body-inner-wrapper`（外层 `--body-wrapper` 是 `overflow:hidden`，设 scrollLeft 无效）

### 3.3 截图规范

```python
from utils.save_screenshot import save_screenshot

save_screenshot(page, "操作前")
self.submit_button.click()
save_screenshot(page, "操作后")
```
截图落在 `picture/screenshots/`，文件名自带时间戳，是排查失败的第一手材料。

## 4. 测试用例编写规范

### 4.1 文件命名

`test_<功能模块>.py`，如 `test_create_contract.py`、`test_goods_transfer.py`

### 4.2 测试类模板（★ 含本项目两个关键约定）

```python
# -*- coding: utf-8 -*-
"""
@Time ： 2026/9/18 09:30
@Auth ： 章豹
@File ：test_xxx.py
@IDE ：PyCharm
@LastEditTime ： 2026/9/18 09:30
"""
import pytest
from playwright.sync_api import expect
from pages.login_page import LoginPage
from pages.xxx_page import XxxPage
from utils.log_print import get_logger
from utils.save_screenshot import save_screenshot


class TestXxx:
    # ★ 约定1：类属性用于跨用例共享数据（如新建后拿到的编号给下一个用例用）
    some_code = None

    @pytest.mark.run(order=1)
    def test_create(self, page, host):
        """新增XXX"""
        LoginPage(page).login(host=host)
        XxxPage(page).create()
        # ★ 约定2：Vue 双向绑定只更新 value property，
        #    get_attribute("value") 拿到 None，必须用 input_value()
        TestXxx.some_code = page.locator("[name='logicContractCode']").input_value()
        get_logger().info(f"新建编号：{TestXxx.some_code}")
        save_screenshot(page, "create_xxx.png")

    @pytest.mark.run(order=2)
    def test_approval(self, page, host):
        """XXX审批"""
        LoginPage(page).login(host=host)
        approval_page = ApprovalPage(page)
        code = TestXxx.some_code          # 从类属性读取
        approval_page.approval_process("补录", code)
        # ★ 约定3：审批后页面状态不自动刷新，必须重新查询再断言
        approval_page.get_contract_details(code)
        expect(page.locator("h3")).to_contain_text("审核通过", timeout=30000)
        save_screenshot(page, "审批结果")
```

### 4.3 编写原则

1. 每个用例只测一个功能点；同一业务流程的多步骤用 `@pytest.mark.run(order=N)` 排序
2. 必须使用 `page` 和 `host` fixture（conftest.py 提供），**不要硬编码环境地址**
3. 断言优先 `playwright expect`（自带自动等待），配 `timeout=` 显式声明
4. 关键步骤加 `save_screenshot`
5. 中文注释写清测试意图

### 4.4 可用的 pytest fixture

| Fixture | 作用域 | 说明 |
|---------|--------|------|
| `page` | function | 每次测试创建新页面（1920x1080） |
| `host` | function | 执行环境（test/uat/dev，读 config/run_env.yml） |
| `browser` | session | 整个会话共用的浏览器实例 |

## 5. 生成新用例的标准工作流（★ 按此执行）

用户通常会**丢一张页面截图**说"给这个页面写用例"。此时**不要凭截图猜定位**，按下面走：

1. **读现有代码**：`pages/public_operation.py`、结构最接近的已有 page 对象和用例，沿用现有风格
2. **写探针脚本**（放 `temp/`，用完删除）：登录 → 导航到目标页面 → dump 真实 DOM
   - 元素类型：`el.tagName`、`aria-controls`、`class`、`placeholder`、`name`
   - 下拉：dump 可见面板的**全部选项文本**（确认选项真实文案，别猜）
   - 表格：dump 表头 `colid` 列表 + 数据行 td 数量（判断是否虚拟渲染）
   - 顺手 `page.screenshot()` 存一张，便于核对
3. **按探针结果写 page 对象 + 测试用例**（头部注释齐全）
4. **`py_compile` 编译检查** → **真跑一次** → 失败就看报错和截图继续修
5. **回归基线用例**：`test_create_user.py`、`test_goods_transfer_in.py` 必须仍然通过
6. 清理 `temp/` 下的探针脚本

## 6. 踩坑清单（血泪总结，写代码前必读）

| # | 坑 | 正确做法 |
|---|---|---|
| 1 | 下拉面板隐藏用**内联 display:none**，没有 `.is-hidden` 类 | 判断可见性用 Playwright `:visible`；选中要定位面板用 `aria-controls` |
| 2 | 对下拉选项用 `scroll_into_view_if_needed()` / Playwright `click()` | **禁止**。会滚动所有祖先容器 → 整个页面跳来跳去、面板漂移、点击超时卡死。必须用 JS click |
| 3 | **多选** el-select 选中后面板**不关闭** | 绝不能用"页面上是否有可见面板"判断当前组件；必须用该组件 input 的 `aria-expanded` |
| 4 | el-select 搜索框全局 `querySelector('.el-select__input')` | 会取到别的组件的搜索框。必须按组件 scope 定位 |
| 5 | 页面同时有"本地保存"和"保存" | `has-text('保存')` 会命中 2 个导致 strict 报错，必须 `re.compile(r"^\s*保存\s*$")` |
| 6 | 用 `get_attribute("value")` 取 Vue input 的值 | 返回 None。必须用 `input_value()` |
| 7 | 全局 `table tbody tr:last-child` 取表格行 | 页面上有十几张 table，会取错。vxe-table 用 `get_vxe_data_row` / `td[colid=...]` |
| 8 | 提交审批确认框当 message-box 找 | 实际是 **`.el-popconfirm`**（"是否提交审批 取消 确定"） |
| 9 | 审批意见框 `[name='comments']` | 实际是 `.el-dialog` 内 `textarea[placeholder='审批意见']`，**没有 name** |
| 10 | 审批按钮全局文本匹配 | 会命中"审批流程/审批退回/审批撤回"。必须限定在弹窗内 + 精确匹配 `^\s*审批\s*$` |
| 11 | 审批通过后直接断言状态 | 页面会**自动跳到"合同簿记-新建"且不刷新**，必须先 `get_contract_details()` 重新查询 |
| 12 | 第二次查询用的是同一个 tab | 切已存在 tab 会**重新挂载组件、清空刚 fill 的搜索值**，填完要 `input_value()` 校验并重填 |
| 13 | 文件头 `FilePath: \ui_auto_project\...` | `\u` 触发 SyntaxError，整个文件 0 用例。用正斜杠 |
| 14 | 选仓库后立刻选品名 | 品名/存货地址等是**联动**加载的，中间要 `wait_for_timeout(2000)` |
| 15 | 表格列 id 写死（如 `col_110`） | 联动后表格会**重建、列 id 变化**，每次填充前重新 `get_vxe_table_by_header` + `get_vxe_colid` |

## 7. 生成代码 Checklist

- [ ] 文件头部注释齐全（且无 `\` 反斜杠路径）
- [ ] `py_compile` 编译通过
- [ ] 下拉用 `select_dropdown_option` / `repetitive_operation`，未自己手写点击逻辑
- [ ] 按钮定位做了精确匹配（避免"本地保存"这类同名干扰）
- [ ] 表格操作走了 vxe-table 专用方法
- [ ] 测试用例使用 `page` / `host` fixture，无硬编码环境地址
- [ ] 跨用例数据用类属性传递，取值用 `input_value()`
- [ ] 关键步骤有截图、有断言
- [ ] 用例真的跑通了一次，且基线用例 `test_create_user.py` / `test_goods_transfer_in.py` 未被破坏
