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
        time.sleep(1)

def get_row_cell_by_header(page, row_locator, header_text):
    """
    根据表头文本定位行中的单元格
    :param page: 页面对象
    :param row_locator: 行元素 Locator
    :param header_text: 列头文本，列名
    :return: 单元格 Locator
    """
    # 获取表格表头所有 th 元素
    ths = page.locator("table thead th")
    col_index = None
    # 遍历表头，查找与 header_text 匹配的列索引
    for i in range(ths.count()):
        if ths.nth(i).text_content().strip() == header_text:
            col_index = i + 1  # 列索引从 1 开始（CSS nth-child 从 1 计数）
            break
    if col_index is None:
        raise Exception(f"未找到列头: {header_text}")
    # 在当前行中定位对应列，在给定的行（row_locator）中，定位该列对应的 td 元素
    cell = row_locator.locator(f"td:nth-child({col_index})")
    return cell

def fill_cell(page, cell, value, field_type='input'):
    """
    填充单元格内的输入控件
    :param page: Playwright 页面对象（用于全局定位，如下拉面板）
    :param cell: 单元格 Locator（如 `td` 元素）
    :param value: 要填入的值（字符串）
    :param field_type: 控件类型，支持 'input', 'combobox', 'spinbutton', 'datepicker'
    """
    if field_type == 'input':
        # 普通文本输入框
        cell.locator("input[type='text'], input:not([role])").first.fill(value)
    elif field_type == 'combobox':
        # 只读下拉框 (Ant Design Select)
        combobox = cell.locator("input[role='combobox']").first
        combobox.click()
        # 等待下拉菜单出现，然后选择选项
        page.locator(".ant-select-dropdown:visible").get_by_text(value, exact=True).click()
    elif field_type == 'spinbutton':
        # 数字输入框 (Ant Design InputNumber)
        cell.locator("input[role='spinbutton']").first.fill(value)
    elif field_type == 'datepicker':
        # 1. 定位日期输入框
        date_input = cell.locator(".ant-picker input")
        if date_input.count() == 0:
            date_input = cell.locator("input[placeholder*='日期']")
        if date_input.count() == 0:
            raise Exception("未找到日期输入框")
        
        date_input.scroll_into_view_if_needed()
        date_input.click()
        
        # 2. 等待日期面板出现
        panel = page.locator(".ant-picker-dropdown:visible, .ant-picker-panel:visible").first
        panel.wait_for(state="visible", timeout=5000)
        
        # 3. 判断是否点击“今天”按钮（当 value 为 "today" 或 None 时）
        if value is None or value.lower() == "today":
            today_btn = panel.locator(".ant-picker-today-btn")
            if today_btn.count() > 0:
                today_btn.click()
                page.wait_for_timeout(300)  # 等待选择完成
                return  # 直接返回，不再执行后续选择
            else:
                raise Exception("未找到“今天”按钮，无法快速选择")
        
        # 4. 解析传入的日期（假设格式 YYYY-MM-DD）
        try:
            year, month, day = value.split('-')
            target_month = int(month)
            target_day = day.lstrip('0')  # 去掉前导零（如 "01" → "1"）
            target_year = int(year)
        except:
            raise ValueError(f"日期格式错误，请使用 YYYY-MM-DD，当前值：{value}")
        
        # 5. 获取当前面板显示的年月（支持 "2026-07" 或 "2026年7月" 等格式）
        header = panel.locator(".ant-picker-header-view").first
        header_text = header.text_content()
        import re
        # 尝试匹配 "2026-07" 或 "2026年7月"
        match = re.search(r'(\d{4})\s*[-年]\s*(\d{1,2})', header_text)
        if not match:
            # 如果无法解析，使用系统当前日期（保守）
            from datetime import datetime
            current_year = datetime.now().year
            current_month = datetime.now().month
        else:
            current_year = int(match.group(1))
            current_month = int(match.group(2))
        
        # 6. 月份切换（如果目标月份与当前不一致）
        if current_year != target_year or current_month != target_month:
            # 计算需要切换的月份差
            # 注意：年份变化需要额外处理（通过点击年份按钮，但 Ant Design 通常使用左右箭头切换月份，跨年时会自动）
            # 简化处理：仅处理同一年内的月份切换，跨年通过连续点击箭头实现
            months_diff = (target_year - current_year) * 12 + (target_month - current_month)
            if months_diff > 0:
                # 向后（增加月份）
                next_btn = panel.locator(".ant-picker-header-next-btn")
                for _ in range(months_diff):
                    next_btn.click()
                    # 等待标题变化到新月份
                    # 使用一个更通用的等待：等待标题不再等于旧的文本
                    page.wait_for_timeout(200)
            else:
                # 向前（减少月份）
                prev_btn = panel.locator(".ant-picker-header-prev-btn")
                for _ in range(-months_diff):
                    prev_btn.click()
                    page.wait_for_timeout(200)
        
        # 7. 定位目标日期单元格并点击（排除其他月份的灰色日期）
        date_cell = panel.locator(f".ant-picker-cell:not(.ant-picker-cell-disabled):not(.ant-picker-cell-other):has-text('{target_day}')")
        # 如果有多个匹配（例如当前月和下个月同一天），取第一个可见的
        date_cell.first.click()
        
        # 8. 等待面板关闭（可选）
        page.wait_for_timeout(300)
    else:
        raise ValueError(f"不支持的字段类型: {field_type}")