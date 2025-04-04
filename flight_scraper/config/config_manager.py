
class ConfigManager:
    """配置管理器，用于统一管理不同类型的配置文件"""

    def __init__(self):
        self._parsers = {}

    def register_parser(self, file_path, parser_class):
        """注册一个配置文件及其对应的解析器"""
        parser = parser_class(file_path)
        self._parsers[file_path] = parser
        return parser.content

    def get_config(self, file_path):
        """获取指定配置文件的内容"""
        if file_path not in self._parsers:
            raise KeyError(f"配置文件未注册：{file_path}")
        return self._parsers[file_path].content

    def reload_config(self, file_path):
        """重新加载指定的配置文件"""
        if file_path not in self._parsers:
            raise KeyError(f"配置文件未注册：{file_path}")
        return self._parsers[file_path].reload()
