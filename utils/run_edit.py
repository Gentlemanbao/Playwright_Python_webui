"""
Author: 章豹
Date: 2025-10-23 17:11:39
LastEditors: Do not edit
LastEditTime: 2026-03-06 15:15:32
FilePath: run_edit.py
"""

from pathlib import Path
from utils.log_print import get_logger
from utils.read_yaml import ReadConfig
logger = get_logger()

def run_edit(env):
    """
    修改执行环境配置文件内容
    :param env: 执行环境
    :return:
    """
    project_root = Path(__file__).parent.parent
    config_path = project_root  / "config" / "run_env.yml"
    logger.info(f"修改执行环境配置文件路径: {config_path}")
    obj = ReadConfig(str(config_path))
    obj.clear_relydata()
    obj.write_config({"run": env})


def run_re():
    """
    获取执行环境
    :return:
    """
    project_root = Path(__file__).parent.parent
    config_path = project_root / "config" / "run_env.yml"
    obj = ReadConfig(str(config_path))
    return obj.read_data("run")



