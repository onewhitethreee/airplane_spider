import json

from config import BaseParseConfig


class JsonParse(BaseParseConfig):
    def _load_config(self):
        """加载配置文件的辅助方法"""
        try:
            with open(self.config_path, "r") as f:
                self._content = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"配置文件未找到：{self._config_path}")
        except json.JSONDecodeError:
            raise ValueError(f"配置文件格式错误：{self._config_path}")
