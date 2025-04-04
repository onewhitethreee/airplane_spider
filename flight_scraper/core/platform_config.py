
class PlatformConfig:
    """
    各种平台的配置类
    """

    def __init__(self, config):
        """
        :param config: 配置文件
        """
        self._config_data = config
        self._load_config()
    
    def _load_config(self):
        """
        加载配置文件，子类实现
        """
        pass

    def api_url(self):
        """
        获取API URL
        """
        raise NotImplementedError("Subclasses should implement this method.")
    
    def search_param(self):
        """
        获取搜索条件
        """
        raise NotImplementedError("Subclasses should implement this method.")
    
    def proxies(self):
        """
        获取代理设置
        """
        raise NotImplementedError("Subclasses should implement this method.")
    