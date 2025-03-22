# booking_spider.py
import os
import sys

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
    

if __name__ == "__main__":
    config_manager = ConfigManager()
    json_config = config_manager.register_parser(
        r"config/configs/config_booking.json", JsonParse
    )
    booking_spider = Booking_spider(json_config)
    