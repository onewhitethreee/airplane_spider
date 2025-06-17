import json
import os
import sys

project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
sys.path.append(project_root)

from flight_scraper.core.platform_config import PlatformConfig


class TripConfig(PlatformConfig):
    """
    Trip平台配置类，继承自PlatformConfig
    """

    def _load_config(self):
        """
        加载配置文件

        """
        trip_config = self._config_data.get("trip", {})
        self._api_url = trip_config.get("api_url")
        self._search_params = trip_config.get("trip_search_condition")
        self._proxies_config = trip_config.get("proxies")

    def get_api_url(self):
        """
        获取API地址

        :return:
        """
        return self._api_url

    def get_search_params(self):
        """
        获取搜索参数
        将True和False转换为true和false, api post格式要求
        :return:
        """
        return {k: True if v == "true" else (False if v == "false" else v) for k, v in self._search_params.items()}

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
    project_root = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
    )
    config_path = os.path.join(project_root, "config", "configs", "config_trip.json")

    print(config_path)
    with open(config_path, "r", encoding="utf-8") as f:
        config_data = json.load(f)

    # 使用加载的配置初始化
    config = TripConfig(config_data)
    print(config.get_api_url())
    print(config.get_search_params())
    print(config.get_proxies_config())
