import unittest
import json
import os
import sys
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
sys.path.append(project_root)
from flight_scraper.platforms.booking.config import BookingConfig


class TestBookingConfig(unittest.TestCase):
    """测试BookingConfig类"""

    def setUp(self):
        """测试前的准备工作"""
        # 准备测试数据
        self.test_config = {
            "booking": {
                "api_url": "https://test-api.example.com",
                "booking_search_condition": {
                    "from": "NYC",
                    "to": "LON",
                    "date": "2025-05-01",
                },
                "proxies": {"http": "http://test-proxy.example.com:8080"},
            }
        }

        # 创建配置对象
        self.config = BookingConfig(self.test_config)

    def test_config_values(self):
        """测试配置值是否正确读取"""
        # 测试API URL
        self.assertEqual(self.config.get_api_url(), "https://test-api.example.com")

        # 测试搜索参数
        expected_params = {"from": "NYC", "to": "LON", "date": "2025-05-01"}
        self.assertEqual(self.config.get_search_params(), expected_params)

        # 测试代理配置
        expected_proxies = {"http": "http://test-proxy.example.com:8080"}
        self.assertEqual(self.config.get_proxies_config(), expected_proxies)


if __name__ == "__main__":
    unittest.main()
