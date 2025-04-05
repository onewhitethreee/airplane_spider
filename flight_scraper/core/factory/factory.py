# flight_scraper/platforms/factory.py
import json
import os
import logging


class ScraperFactory:
    """爬虫工厂类，负责创建不同平台的爬虫实例"""

    @staticmethod
    def create_scraper(platform_name, config=None):
        """创建指定平台的爬虫实例

        Args:
            platform_name: 平台名称
            config: 配置数据，None则自动加载

        Returns:
            FlightScraper: 爬虫实例
        """
        # 如果没有提供配置，加载配置
        if config is None:
            config = ScraperFactory._load_config(platform_name)

        # 根据平台名称创建对应的爬虫实例
        if platform_name.lower() == "booking":
            from flight_scraper.platforms.booking.scraper import BookingScraper
            from flight_scraper.platforms.booking.config import BookingConfig
            platform_config = BookingConfig(config)
            return BookingScraper(platform_config)
        """
        Booking多日期搜索。
        """
        if platform_name.lower() == "booking_multi_date":
            from flight_scraper.platforms.booking.multi_date_scraper import MultiDateBookingScraper
            from flight_scraper.platforms.booking.config import BookingConfig
            platform_config = BookingConfig(config)
            return MultiDateBookingScraper(platform_config)
        # 添加其他平台支持...

        else:
            raise ValueError(f"不支持的平台: {platform_name}")

    @staticmethod
    def _load_config(platform_name):
        """加载指定平台的配置

        Args:
            platform_name: 平台名称

        Returns:
            dict: 配置数据
        """
        # 获取项目根目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))

        # 配置文件路径
        if platform_name.lower() == "booking" or platform_name.lower() == "booking_multi_date":
            config_path = os.path.join(
                project_root, "config", "configs", f"config_booking.json"
            )
        else:
            config_path = os.path.join(
                project_root, "config", "configs", f"config_{platform_name.lower()}.json"
            )

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"加载{platform_name}配置文件失败: {e}")
            raise
