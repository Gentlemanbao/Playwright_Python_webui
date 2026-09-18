# -*- coding: utf-8 -*-
"""
@Time ： 2026/7/6 17:30
@Auth ： 章豹
@File ：public_operation.py
@IDE ：PyCharm
@LastEditTime ： 2026/9/16 17:30
"""
import time


def _el_select_selected_label(select_locator):
    """
    读取 el-select 当前已选中的展示文本。
    - 单选：渲染在 .el-select__placeholder，未选中时该元素带 is-transparent 类；
    - 多选：没有 placeholder 元素，选中值是组件内的 .el-tag 文本。
    未选中返回 ''；结构不存在/无法判断时返回 None（视为校验通过）。
    """
    try:
        return select_locator.evaluate(
            """el => {
                const tags = Array.from(el.querySelectorAll('.el-tag'))
                    .map(t => (t.textContent || '').trim()).filter(t => t);
                if (tags.length) return tags.join(',');
                const ph = el.querySelector('.el-select__placeholder');
                if (ph) {
                    if (ph.classList.contains('is-transparent')) return '';
                    return (ph.textContent || '').trim();
                }
                // 多选未选中：没有 placeholder 也没有 tag，用整体文本兜底
                const t = (el.innerText || '').replace(/\\s+/g, '').trim();
                return (t && t !== '请选择') ? t : '';
            }"""
        )
    except Exception:
        return None


def _el_select_expanded(select_locator):
    """
    该组件自己的下拉面板是否已展开（input 的 aria-expanded）。
    绝不能用"页面上是否有可见面板"判断：多选组件选中后面板保持打开，
    会误认为下一个 select 的面板已开，导致在别人的面板里找选项而串台。
    """
    try:
        return select_locator.evaluate(
            """el => {
                const input = el.querySelector('input');
                return !!input && input.getAttribute('aria-expanded') === 'true';
            }"""
        )
    except Exception:
        return False


def _el_select_own_panel(page, select_locator):
    """
    通过 input 的 aria-controls 拿到该组件自己下拉面板的元素，
    精确到组件级，避免误用其它 select 遗留的可见面板。
    面板未打开/找不到时返回 None。
    """
    try:
        pid = select_locator.evaluate(
            """el => {
                const input = el.querySelector('input');
                return input ? input.getAttribute('aria-controls') : null;
            }"""
        )
    except Exception:
        return None
    if not pid:
        return None
    panel = page.locator(f'[id="{pid}"]').last
    if panel.count() == 0 or not panel.is_visible():
        return None
    return panel


def select_dropdown_option(page, select_locator, text, timeout=8000):
    """
    Element Plus el-select 通用选项选择（可靠版）
    :param page: Playwright page 对象
    :param select_locator: .el-select 组件的 locator
    :param text: 要选择的选项文本（包含匹配）
    :param timeout: 等待下拉面板出现的超时时间（毫秒）

    关键点：
    1. 用 aria-expanded 判断该组件自己的面板是否展开、用 aria-controls
       精确拿到自己的面板元素；多选组件选中后面板不关闭，全局"最后一个
       可见面板"会串到别人的面板。
    2. 若组件可搜索(filterable)，先在组件内部的 .el-select__input
       输入关键词触发过滤/远程加载，选项才会出现。
    3. 选中动作必须用 JS 点击（在面板元素内部完成），
       绝不能用 scroll_into_view_if_needed / Playwright click——
       它们会滚动页面上所有祖先容器，导致整个页面来回跳动、
       下拉面板定位失效后点击超时卡死。
    4. 选中后校验展示文本是否真的变化（JS click 偶发打在 Vue 重渲染前的
       旧节点上而静默失效），未生效自动重试；找不到选项时抛出异常并列出
       当前面板的全部选项，便于排查。
    """
    PICK_JS = """(el, arg) => {
            const items = Array.from(el.querySelectorAll('li.el-select-dropdown__item'));
            const cands = items.filter(i =>
                !i.classList.contains('is-disabled') &&
                !i.classList.contains('is-loading') &&
                i.textContent.trim()
            );
            const target = cands.find(i => i.textContent.includes(arg.text));
            if (target) {
                target.click();
                return { ok: true };
            }
            return { ok: false, options: cands.map(i => i.textContent.trim()) };
        }"""

    last_options = []
    for attempt in range(3):
        # 打开该组件自己的下拉面板（aria-expanded 为准，多选遗留面板不影响判断）
        if not _el_select_expanded(select_locator):
            select_locator.click()
        # 等自己的面板可见
        panel = None
        deadline = time.time() + timeout / 1000
        while time.time() < deadline:
            panel = _el_select_own_panel(page, select_locator)
            if panel is not None:
                break
            page.wait_for_timeout(150)
        if panel is None:
            # 面板没开出来，重试
            continue

        # 若组件内有搜索输入框（filterable），输入关键词触发过滤
        search_input = select_locator.locator(".el-select__input").first
        if search_input.count() > 0:
            try:
                search_input.click(timeout=2000)
                search_input.fill("")
                page.keyboard.type(text, delay=80)
            except Exception:
                pass  # 不可搜索就按原始列表匹配
            # 等过滤/远程加载完成（列表刷新）
            page.wait_for_timeout(800)

        # 在自己的面板内部用 JS 查找并点击匹配项（不会滚动页面）
        result = panel.evaluate(PICK_JS, {"text": text})

        if not result["ok"] and search_input.count() == 0:
            # 没有搜索框且首屏没有匹配项：只滚动面板自己的内层列表（虚拟列表兜底），
            # 不滚动页面
            for _ in range(10):
                can_scroll = panel.evaluate(
                    """(el) => {
                        const w = el.querySelector('.el-select-dropdown__wrap');
                        if (!w) return false;
                        w.scrollTop += w.clientHeight;
                        return w.scrollTop < w.scrollHeight - w.clientHeight;
                    }"""
                )
                page.wait_for_timeout(200)
                result = panel.evaluate(PICK_JS, {"text": text})
                if result["ok"]:
                    break
                if not can_scroll:
                    break

        if not result["ok"]:
            # 面板里确实没有该选项，重试也不会有
            last_options = result.get("options", [])
            page.keyboard.press("Escape")
            break

        # 选中后校验是否真的生效：JS click 可能打在 Vue 重渲染前的旧节点上而静默失效
        page.wait_for_timeout(500)
        label = _el_select_selected_label(select_locator)
        if label is None or label:
            return  # 无法校验（结构不存在）或已选中

    raise Exception(
        f"下拉选择 '{text}' 未生效，当前面板全部选项: {sorted(set(o for o in last_options if o))}"
    )


def repetitive_operation(page, page_obj, input_text=None, is_click=False):
    """
    重复操作方法，智能适配普通 input 和 Element Plus Select 组件
    :param page: Playwright page 对象
    :param page_obj: 页面元素 locator
    :param input_text: 要输入/选择的文本
    :param is_click: True 表示先点击再输入（用于日期选择器等），False 表示下拉选择/输入
    
    核心策略：Element Plus el-select 是可搜索的（filterable），
    正确做法是 click 打开下拉 → 在 select 内部的 .el-select__input 里 fill 搜索词
    → 等过滤 → 选选项。不能只看固定渲染的前几个选项。
    """
    # 判断 locator 类型：如果是 el-select 组件（div），走下拉选择流程
    tag_name = page_obj.evaluate("el => el.tagName").lower()
    if tag_name == 'div':
        # Element Plus Select 组件：click 打开下拉 → 组件内搜索过滤 → 选选项
        select_dropdown_option(page, page_obj, input_text, timeout=8000)
    else:
        # 普通 input：click → fill → Enter
        if is_click:
            page_obj.click(force=True)
            time.sleep(0.5)
        # page.wait_for_selector(".el-select-dropdown:visible", state="visible")
        page_obj.fill(input_text)
        page.keyboard.press("ArrowDown")
        page.keyboard.press("Enter")
        time.sleep(0.5)



def get_vxe_table_by_header(page, marker_header="未选仓库备注"):
    """
    按特征列头定位 vxe-table。
    页面上可能存在多个 vxe-table，且联动后表格会重建（列 id 会变），
    因此不能用 .vxe-table.first 这种位置定位。
    """
    return page.locator(".vxe-table").filter(
        has=page.locator("th", has_text=marker_header)
    ).first


def get_vxe_colid(table, header_text):
    """
    在 vxe-table 中按表头文本取列 colid（忽略空白差异，排除 fixed--hidden 的克隆列）
    :param table: .vxe-table 根元素的 locator
    :param header_text: 列头文本
    :return: colid 字符串（如 col_103），未找到返回 None
    """
    return table.evaluate(
        """(el, header) => {
            const norm = s => (s || '').replace(/\\s+/g, '');
            const th = Array.from(el.querySelectorAll('.vxe-table--header-wrapper th'))
                .find(t => !t.classList.contains('fixed--hidden') && norm(t.innerText) === norm(header));
            return th ? th.getAttribute('colid') : null;
        }""",
        header_text,
    )


def get_vxe_data_row(table):
    """
    取 vxe-table 的数据行（排除"合计"行）。
    vxe-table 的表头/数据行/固定列分属不同 <table>，
    绝不能全局用 `table tbody tr:last-child` 定位。
    """
    rows = table.locator(".vxe-table--body-wrapper tbody tr")
    for i in range(rows.count()):
        r = rows.nth(i)
        if "合计" not in (r.inner_text() or ""):
            return r
    raise Exception("未找到 vxe-table 数据行（可能尚未点击新增按钮）")


def vxe_scroll_to_column(page, table, row, colid):
    """
    横向滚动 vxe-table，使目标列被渲染出来。
    该表格开启了列虚拟化：只有可视区内的列才会生成 td，未渲染的列直接定位会超时。
    真正的横向滚动容器是 .vxe-table--body-inner-wrapper
    （.vxe-table--body-wrapper 是 overflow:hidden，设置 scrollLeft 无效）。
    """
    def rendered():
        return row.locator(f"td[colid='{colid}']").count() > 0

    if rendered():
        return
    # 表头是全量渲染的，用表头列的 offsetLeft 估算目标 scrollLeft
    target_left = table.evaluate(
        """(el, colid) => {
            const th = Array.from(el.querySelectorAll('.vxe-table--header-wrapper th'))
                .find(t => t.getAttribute('colid') === colid);
            return th ? th.offsetLeft : -1;
        }""",
        colid,
    )
    # 逐档尝试：目标列左侧 -600 开始，每次 +300（列渲染窗口约 1500px，不会跳过）
    start = 0
    if target_left > 0:
        start = max(0, target_left - 600)
    for sl in [start + i * 300 for i in range(30)]:
        table.evaluate(
            """(el, sl) => {
                el.querySelectorAll('.vxe-table--body-inner-wrapper').forEach(w => { w.scrollLeft = sl; });
            }""",
            sl,
        )
        page.wait_for_timeout(200)
        if rendered():
            return
    raise Exception(f"横向滚动后仍未渲染出列 {colid}")


def vxe_fill_cell(page, table, header_text, value, field_type='combobox'):
    """
    填写 vxe-table 单元格。该表格为"点击单元格激活编辑"模式：
    单击后单元格内才渲染 el-select / el-input-number / 日期控件；
    并且列是虚拟渲染的，需先横向滚动让目标列出现。
    每次调用都会重新解析列 id 和数据行（表格可能因联动而重建）。
    :param page: Playwright page 对象
    :param table: .vxe-table 根元素 locator（每次调用前重新定位）
    :param header_text: 列头文本
    :param value: 要填写的值
    :param field_type: 'combobox' 下拉 / 'spinbutton' 数字 / 'datepicker' 日期
    """
    colid = get_vxe_colid(table, header_text)
    if not colid:
        raise Exception(f"货物明细表中未找到列: {header_text}")
    row = get_vxe_data_row(table)
    vxe_scroll_to_column(page, table, row, colid)
    cell = row.locator(f"td[colid='{colid}']")
    cell.scroll_into_view_if_needed()
    cell.click()
    page.wait_for_timeout(600)

    if field_type == 'combobox':
        sel = cell.locator(".el-select").first
        if sel.count() == 0:
            raise Exception(f"列 '{header_text}' 点击后未渲染下拉控件")
        select_dropdown_option(page, sel, value)
    elif field_type == 'spinbutton':
        inp = cell.locator("input").first
        inp.click()
        inp.fill(str(value))
        page.keyboard.press("Tab")  # 失焦提交 vxe 单元格编辑
    elif field_type == 'datepicker':
        inp = cell.locator("input").first
        inp.click()
        inp.fill(str(value))
        page.keyboard.press("Enter")
    else:
        raise ValueError(f"不支持的 vxe 单元格类型: {field_type}")
    page.wait_for_timeout(400)
    return colid
