import os
import sys
import json
from distutils.command.config import config

project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
sys.path.append(project_root)

from flight_scraper.core.platform_config import PlatformConfig


class BookingConfig(PlatformConfig):

    def _load_config(self):
        """
        加载配置文件

        """
        booking_config = self._config_data.get("booking", {})
        self._api_url = booking_config.get("api_url")
        self._search_params = booking_config.get("booking_search_condition")
        self._proxies_config = booking_config.get("proxies")

    def get_api_url(self):
        """
        获取API地址

        :return:
        """
        return self._api_url

    def get_search_params(self):
        """
        获取搜索参数

        :return:
        """
        return self._search_params

    def get_proxies_config(self):
        """
        获取代理配置

        :return:
        """
        return self._proxies_config


if __name__ == "__main__":
    # 从文件加载配置
    print("加载配置文件...")

    current_file = os.path.abspath(__file__)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))
    config_path = os.path.join(project_root, "config", "configs", "config_booking.json")

    print(config_path)
    with open(
        config_path, "r", encoding="utf-8"
    ) as f:
        config_data = json.load(f)

    # 使用加载的配置初始化
    config = BookingConfig(config_data)
    print(config.get_api_url())
    print(config.get_search_params())
    print(config.get_proxies_config())
