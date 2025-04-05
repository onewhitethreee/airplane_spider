# flight_scraper/core/abstract_scraper.py
from abc import ABC, abstractmethod


class FlightScraper(ABC):
    """
    航班爬虫的抽象基类，定义所有爬虫实现必须提供的接口
    """

    def __init__(self, config):
        """
        初始化爬虫

        Args:
            config: 配置对象或配置数据
        """
        self._config = config
        self._initialize_common()

    def _initialize_common(self):
        """初始化所有爬虫通用的属性"""
        self._headers = self._initialize_headers()
        self._proxies = self._initialize_proxies()

    @abstractmethod
    def _initialize_headers(self):
        """初始化HTTP请求头"""
        pass

    @abstractmethod
    def _initialize_proxies(self):
        """初始化代理设置"""
        pass

    @abstractmethod
    def requests_flight_info(self):
        """获取航班信息"""
        pass

    @abstractmethod
    def parse_flights(self):
        """解析航班数据"""
        pass

    @abstractmethod
    def parse_price(self, index=0):
        """
        解析价格信息

        Args:
            index: 航班索引，默认为0

        Returns:
            包含价格信息的字典
        """
        pass

    @abstractmethod
    def parse_time(self, page=0):
        """
        解析时间信息

        Args:
            page: 页码，默认为0

        Returns:
            包含时间信息的字典
        """
        pass

    @abstractmethod
    def parse_airport(self, page=0):
        """
        解析机场信息

        Args:
            page: 页码，默认为0

        Returns:
            包含机场信息的字典
        """
        pass

    @abstractmethod
    def parse_airline(self, page=0):
        """
        解析航空公司信息

        Args:
            page: 页码，默认为0

        Returns:
            包含航空公司信息的字典
        """
        pass

    @abstractmethod
    def parse_luggage_allowance(self, page=0):
        """
        解析行李额信息

        Args:
            page: 页码，默认为0

        Returns:
            包含行李额信息的字典
        """
        pass

    @abstractmethod
    def generate_booking_link(self, page=0):
        """
        生成预订链接

        Args:
            page: 页码，默认为0

        Returns:
            预订链接字符串
        """
        pass

    @abstractmethod
    def run(self):
        """
        运行爬虫流程

        Returns:
            处理结果
        """
        pass
