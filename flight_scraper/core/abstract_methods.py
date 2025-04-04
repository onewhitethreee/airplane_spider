# 抽象类的定义。所有的的基类都需要实现这个类。省去命名

from abc import abstractmethod


class AbstractScraper:
    def __init__(self, config):
        """
        :param config: 配置文件
        """
        self.config = config
        self._data_loaded = False

    @property
    @abstractmethod
    def api_url(self):
        """
        :return: API URL
        """
        pass

    @property
    @abstractmethod
    def search_condition(self):
        """
        :return: 搜索条件
        """
        pass

    @property
    @abstractmethod
    def proxies(self):
        """
        :return: 代理设置
        """
        pass

    @abstractmethod
    def _initialize_headers(self):
        """
        初始化请求头
        """
        pass

    @abstractmethod
    def get_flight_data(self):
        """
        获取航班数据
        """
        pass

    @abstractmethod
    def parse_flight_data(self, index):
        """
        解析航班数据
        """
        pass

    @abstractmethod
    def run(self):
        """
        运行爬虫
        """
        pass
