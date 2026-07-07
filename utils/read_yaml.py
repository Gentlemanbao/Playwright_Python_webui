"""
@Time ： 2026/7/6 17:30
@Auth ： 章豹
@File ：read_yaml.py
@IDE ：PyCharm
@LastEditTime ： 2026/7/6 17:30
"""
import os
import yaml
from utils.log_print import get_logger
logger = get_logger()


class ReadConfig:
    def __init__(self, yaml_file):
        self.yaml_file = yaml_file
        self._validate_file()

    def _validate_file(self):
        """
        验证文件是否存在
        :return:
        """
        if not os.path.exists(self.yaml_file):
            error_msg = f"配置文件不存在: {self.yaml_file}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        if not os.path.isfile(self.yaml_file):
            error_msg = f"路径不是文件: {self.yaml_file}"
            logger.error(error_msg)
            raise IsADirectoryError(error_msg)

    def read_config(self):
        """
        读取yaml文件内容
        :return: 配置数据字典
        """
        try:
            with open(self.yaml_file, "r", encoding="utf-8") as f:
                config_data = yaml.load(stream=f, Loader=yaml.FullLoader)
                if config_data is None:
                    logger.warning(f"配置文件为空: {self.yaml_file}")
                    return {}
                return config_data
        except yaml.YAMLError as e:
            error_msg = f"解析YAML文件失败: {self.yaml_file}, 错误: {str(e)}"
            logger.error(error_msg)
            raise
        except Exception as e:
            error_msg = f"读取配置文件失败: {self.yaml_file}, 错误: {str(e)}"
            logger.error(error_msg)
            raise

    def write_config(self, data):
        """
        yaml文件内容写入
        :param data: 传写入的内容，注意是字典格式的
        :return:
        """
        try:
            if not isinstance(data, dict):
                error_msg = f"写入数据必须是字典类型，当前类型: {type(data)}"
                logger.error(error_msg)
                raise TypeError(error_msg)
            
            with open(self.yaml_file, "a", encoding="utf-8") as f:
                yaml.dump(data, stream=f, allow_unicode=True)
            logger.info(f"成功写入配置到文件: {self.yaml_file}")
        except Exception as e:
            error_msg = f"写入配置文件失败: {self.yaml_file}, 错误: {str(e)}"
            logger.error(error_msg)
            raise

    def clear_relydata(self):
        """
        清空依赖数据
        :return:
        """
        try:
            with open(self.yaml_file, "w") as rfile:
                rfile.truncate(0)
            logger.info(f"成功清空配置文件: {self.yaml_file}")
        except Exception as e:
            error_msg = f"清空配置文件失败: {self.yaml_file}, 错误: {str(e)}"
            logger.error(error_msg)
            raise

    def read_data(self, key):
        """
        读取yaml文件内容，并且指定key取指定的value
        :param key: 配置键名
        :return: 配置值
        """
        try:
            config_data = self.read_config()
            if key not in config_data:
                error_msg = f"配置文件中不存在键: {key}"
                logger.error(error_msg)
                raise KeyError(error_msg)
            return config_data[key]
        except KeyError:
            raise
        except Exception as e:
            error_msg = f"读取配置项失败: {key}, 错误: {str(e)}"
            logger.error(error_msg)
            raise
