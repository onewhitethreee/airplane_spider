# booking_spider.py
import os
import sys
import requests
import json
# 获取项目根目录路径
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.append(project_root)

from config.json_parse import JsonParse
from config.config_manager import ConfigManager
from airplane_platform.booking import Booking

class Booking_spider(Booking):
    """
    初始化booking模块的配置信息
    内有atributes：booking_search_condition, booking_api_url
    """
    def __init__(self, booking_search_condition):
        super().__init__(booking_search_condition)
        self._headers = self._initialize_headers()

    def _initialize_headers(self):
        """初始化headers需要的信息"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        }
        return headers
    
    def _initialize_proxies(self):
        """初始化proxies需要的信息. 暂时搁置. 有一个self._proxies属性，里面有x个代理信息"""
        self._proxies = None # 暂时搁置

    def get_flight_info(self):
        """获取航班信息"""
        url = self.booking_api_url
        params = self.booking_search_condition
        response = requests.get(url, params=params, headers=self._headers, proxies=self._proxies, verify=False)
        with open("flights.json", "w", encoding='utf-8') as f:
            f.write(response.text)

    def rm_flights_json(self):
        """删除flights.json文件"""
        if os.path.exists("flights.json"):
            os.remove("flights.json")

    def __del__(self):
        """析构函数，删除flights.json文件"""
        # self.rm_flights_json()
        pass
    
    def __str__(self):
        """ 重写__str__方法，返回booking_search_condition, booking_api_url, proxies"""
        return f"booking_search_condition: {self.booking_search_condition}, booking_api_url: {self.booking_api_url}, proxies: {self._proxies}"
    
    def parse_flights(self):
        """解析flights.json文件"""
        with open("flights.json", "r", encoding='utf-8') as f:
            flights = json.load(f)
        return flights
    
    def parse_price(self):
        """解析价格"""
        pass

    def parse_time(self):
        """解析飞行时间"""
        pass
    
    def parse_airport(self):
        """解析机场"""
        pass

    def parse_airline(self):
        """解析航空公司"""
        pass

    def parse_luggage_allowance(self):
        """解析行李额"""
        pass
if __name__ == "__main__":
    config_manager = ConfigManager()
    json_config = config_manager.register_parser(
        r"config/configs/config_booking.json", JsonParse
    )
    booking_spider = Booking_spider(json_config)
    # booking_spider.get_flight_info()
