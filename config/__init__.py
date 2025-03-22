from abc import abstractmethod, ABC

class BaseParseConfig(ABC):
    def __init__(self, config_path):
        self._config_path = config_path  # 保存配置文件路径
        self._content = None  # 使用下划线前缀的私有属性
        self._load_config()  # 在初始化时加载配置

    @abstractmethod
    def _load_config(self):
        pass
    @property
    def config_path(self):
        return self._config_path
    @property
    def content(self):
        return self._content
    @content.setter
    def content(self, value):
        self._content = value
    

    
