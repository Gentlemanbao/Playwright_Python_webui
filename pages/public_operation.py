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