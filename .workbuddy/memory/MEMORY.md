# 项目长期笔记：ui_auto_project

## 技术栈与结构
- Playwright(sync) + pytest UI 自动化，被测系统：银河德睿（Vue3 + Element Plus + Vben Admin），测试环境 http://192.168.100.147/biz
- conftest.py：session 级 browser（headless=False, slow_mo=500），viewport 1920x1080；host 从 config/run_env.yml 读取
- pages/public_operation.py 是公共操作层；页面继承模式：Page Object 在 __init__ 里定义 locator，方法串操作

## 关键约定（踩坑总结）
- Element Plus 下拉（el-select）选中**必须用 JS 点击选项**（在可见面板元素内部 evaluate），禁止对选项用 scroll_into_view_if_needed / Playwright click——会滚动页面所有祖先容器导致页面跳动、面板定位漂移、点击超时卡死
- **多选 el-select 选中后面板不关闭**：绝不能用"页面上是否有可见面板"判断当前 select 的面板（会串到别人的面板，在'标准/非标准'面板里找'客户授信'这种错）。正确做法：用 input 的 `aria-expanded` 判断本组件面板是否展开、用 `aria-controls` 拿本组件自己的面板 id 精确定位（见 select_dropdown_option）
- el-select 选中后校验：单选看 `.el-select__placeholder`（未选中带 is-transparent），多选看 `.el-tag` 文本；JS click 偶发打在 Vue 重渲染前的旧节点上静默失效，select_dropdown_option 已内置校验+重试 3 次
- 隐藏的下拉面板是内联 display:none，没有 .is-hidden 类；筛选可见面板要用 Playwright 的 `.el-select-dropdown:visible`
- el-select 的搜索框是组件内部的 `.el-select__input`，必须按组件 scope 定位，不能全局 querySelector（会取到别的组件的）
- 定位表单控件：用 `[name='xxx']` + `xpath=ancestor::div[contains(@class,'el-select') and not(contains(@class,'el-select__'))]` 找最外层组件
- 货物明细表是 **vxe-table**：点击单元格激活编辑、列虚拟渲染（滚动容器 `.vxe-table--body-inner-wrapper`）、按 colid 定位 td；用 `get_vxe_table_by_header`（特征列头"未选仓库备注"）定位表格，禁止全局 `table tbody tr:last-child`
- 页面同时有"本地保存"和"保存"按钮，定位保存必须精确匹配 `^\s*保存\s*$`
- Vue input 的值用 `input_value()` 取，`get_attribute("value")` 返回 None
- **审批流程（approval_page.py）**：提交审批确认框是 `.el-popconfirm`（"是否提交审批 取消 确定"），不是 message-box/dialog；审批意见框是 `.el-dialog` 内 `textarea[placeholder='审批意见']`（无 name 属性），审批按钮必须限定弹窗内精确匹配 `^\s*审批\s*$`；补录流程=业务员→货权管理部复核两级；**审批通过后页面自动跳到"合同簿记-新建"且状态不自动刷新**，断言前必须重新查询；再次点击菜单切已存在 tab 会重新挂载组件、清空刚 fill 的搜索值，查询后要校验搜索框值并等 h3 出现合同号
- **koroFileHeader 插件坑**：自动生成的文件头 `FilePath: \ui_auto_project\...` 里的 `\u` 会被 Python 当 unicode 转义导致整个文件 SyntaxError（0 用例收集），FilePath 必须用正斜杠
- 跑测试用系统 Python 3.11.9；pytest.ini 的 testpaths 指向当前调试的用例
- 稳定基线用例：test_create_user.py、test_goods_transfer_in.py；test_create_yikoujia_contract.py 两个用例（创建+审批）已全部调通（2026-09-17，2 passed，合同 20260917-BDFZ-SFNSS005 创建并审核通过）

## 协作方式与扩展用例约定（用户明确要求）
- 用户的 AI coding 工具是 **Trae**；项目内置了 Trae skill：**`D:\期现项目资料\ui_auto_project\.trae\skills\playwright-ui-auto\SKILL.md`**
  → **写新页面对象/新用例前必须先读这个 skill**（2026-09-18 已由我更新到与真实代码一致：修正了"Ant Design"、`utils/public_operation.py` 等错误描述，补齐 vxe-table 与 15 条踩坑清单）
- 用户后续会直接**发一张页面截图**要求新增自动化用例 → 沿用当前代码结构写（Page Object 放 `pages/`，用例放 `test_cases/`，公共方法只加到 `pages/public_operation.py`）
- **不要凭截图猜定位**：标准流程 = 先读 skill 与最接近的现有 page → 在 `temp/` 写探针 dump 真实 DOM（元素类型/name/placeholder/下拉全部选项/表格 colid 列表）→ 写代码 → py_compile → 真跑一次 → 回归基线用例 → 删掉探针
- `utils/` 是用户自己开发的工具类，**不要改动**（只读复用）
- 用例命名与排序遵循现有风格：`@pytest.mark.run(order=N)`，跨用例数据用类属性传递，取值用 `input_value()`
