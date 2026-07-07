# -*- coding: utf-8 -*-
"""
@Time ： 2026/7/6 17:30
@Auth ： 章豹
@File ：remove_file.py
@IDE ：PyCharm
@LastEditTime ： 2026/7/6 17:30
"""


import os
import shutil
import datetime


class RemoveFile:
    def __init__(self, filepath):
        """
        初始化方法
        :param filepath: 传需要删除文件的文件夹路径
        """
        self.filepath = filepath

    def remove_file(self):
        """
        删除指定文件夹下所有的文件
        :return:
        """
        if os.path.exists(self.filepath):
            f_list = os.listdir(self.filepath)
            for i in f_list:
                os.remove(self.filepath + "/" + i)

    def clear_file(self):
        del_list = os.listdir(self.filepath)
        for f in del_list:
            file_path = os.path.join(self.filepath, f)
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)

    def remove_time_file(self):
        """
        删除创建日期距离当前时间大于7天的文件
        :return:
        """
        if os.path.exists(self.filepath):
            f_list = os.listdir(self.filepath)
            now_time = datetime.datetime.now().strftime('%Y-%m-%d')
            for i in f_list:
                timestamp = os.path.getctime(self.filepath+"/"+i)
                date = datetime.datetime.fromtimestamp(timestamp)
                date = date.strftime("%Y-%m-%d")
                d1 = now_time.split(sep="-")
                d2 = date.split(sep="-")
                d1_time = datetime.datetime(int(d1[0]), int(d1[1]), int(d1[2]))
                d2_time = datetime.datetime(int(d2[0]), int(d2[1]), int(d2[2]))
                count_time = (d1_time - d2_time).days
                if count_time >= 7:
                    os.remove(self.filepath + "/" + i)


def clear_file(file_path, is_data='否'):
    """
    删除文件夹所有的文件,保留该文件夹下的文件夹
    :param file_path: 传需要删除文件的文件夹路径
    :param is_data: 是否删除该文件夹下的文件夹，传非否那就删除file_path下所有的文件以及文件夹，反正指删除文件夹所有的文件,保留该文件夹下的文件夹
    :return:
    """
    if os.path.exists(file_path):
        f_list = os.listdir(file_path)
        for i in f_list:
            file_data = file_path + "\\" + i
            if os.path.isfile(file_data):
                os.remove(file_path+"/"+i)
            else:
                if is_data != '否':
                    shutil.rmtree(file_data)
                else:
                    clear_file(file_data)