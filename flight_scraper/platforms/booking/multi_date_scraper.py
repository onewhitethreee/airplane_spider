# flight_scraper/platforms/booking/multi_date_scraper.py
import os
import sys
import json
import logging
from datetime import datetime, timedelta
import copy
from typing import List, Dict, Any, Tuple, Optional

from flight_scraper.core.factory.factory import ScraperFactory

# 获取项目根目录路径
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.append(project_root)

from flight_scraper.platforms.booking.scraper import BookingScraper
from flight_scraper.platforms.booking.config import BookingConfig


class MultiDateBookingScraper:
    """支持多日期爬取的Booking航班爬虫"""

    def __init__(self, platform_config):
        """
        初始化多日期爬虫

        Args:
            platform_config: BookingConfig实例或原始配置数据
        """
        # 检查传入的是 BookingConfig 实例还是配置字典
        if hasattr(platform_config, 'get_api_url') and callable(platform_config.get_api_url):
            # 是 BookingConfig 实例
            self._original_config = platform_config
        elif isinstance(platform_config, dict) and 'booking' in platform_config:
            # 是配置字典
            from flight_scraper.platforms.booking.config import BookingConfig
            self._original_config = BookingConfig(platform_config)
        else:
            # 处理其他情况，比如从BookingScraper获取配置
            if hasattr(platform_config, '_platform_config'):
                self._original_config = platform_config._platform_config
            else:
                # 最后的尝试，从工厂获取默认配置
                from flight_scraper.core.factory.factory import ScraperFactory
                booking_config = ScraperFactory._load_config("booking")
                from flight_scraper.platforms.booking.config import BookingConfig
                self._original_config = BookingConfig(booking_config)

        self._results = []
        self._date_configs = []

    def generate_date_range(self, start_date_str: str, days_range: int = 10,
                            return_days: int = 36) -> List[Tuple[str, str]]:
        """
        生成日期范围

        Args:
            start_date_str: 开始日期，格式为 YYYY-MM-DD
            days_range: 出发日期范围天数，默认为10天
            return_days: 返程天数，默认为36天

        Returns:
            出发和返程日期对的列表，每个元素为 (depart_date, return_date)
        """
        date_pairs = []
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")

        for i in range(days_range):
            depart_date = start_date + timedelta(days=i)
            return_date = depart_date + timedelta(days=return_days)

            date_pairs.append((
                depart_date.strftime("%Y-%m-%d"),
                return_date.strftime("%Y-%m-%d")
            ))

        return date_pairs

    def prepare_date_configs(self, date_pairs: List[Tuple[str, str]]) -> None:
        """
        为每个日期对准备配置

        Args:
            date_pairs: 出发和返程日期对的列表
        """
        self._date_configs = []

        # 获取原始搜索参数
        original_params = self._original_config.get_search_params()

        for depart_date, return_date in date_pairs:
            # 创建新的配置副本
            config_copy = copy.deepcopy(self._original_config._config_data)

            # 更新日期
            config_copy["booking"]["booking_search_condition"]["depart"] = depart_date
            config_copy["booking"]["booking_search_condition"]["return"] = return_date

            # 保存修改后的配置
            self._date_configs.append(config_copy)

    def scrape_all_dates(self) -> List[Dict[str, Any]]:
        """
        爬取所有日期的航班信息

        Returns:
            所有日期的航班信息列表
        """
        self._results = []

        for i, config in enumerate(self._date_configs):
            try:
                logging.info(f"爬取第 {i + 1}/{len(self._date_configs)} 个日期组合")

                # 创建爬虫实例
                scraper = ScraperFactory.create_scraper("booking")

                # 保存配置中的日期信息
                depart_date = config["booking"]["booking_search_condition"]["depart"]
                return_date = config["booking"]["booking_search_condition"]["return"]

                # 获取航班信息
                scraper.requests_flight_info()
                scraper.parse_flights()

                # 加载数据
                if scraper.load_data() and scraper._processed_offers:
                    # 如果有结果，处理前5个最便宜的选项
                    max_options = min(5, len(scraper._processed_offers))

                    for j in range(max_options):
                        price_info = scraper.parse_price(j)
                        time_info = scraper.parse_time(j)
                        airport_info = scraper.parse_airport(j)
                        airline_info = scraper.parse_airline(j)
                        luggage_info = scraper.parse_luggage_allowance(j)
                        booking_link = scraper.generate_booking_link(j)

                        # 组合结果
                        result = {
                            "depart_date": depart_date,
                            "return_date": return_date,
                            "price": price_info,
                            "time": time_info,
                            "airport": airport_info,
                            "airline": airline_info,
                            "luggage": luggage_info,
                            "booking_link": booking_link,
                            "flight_index": j
                        }

                        self._results.append(result)
                else:
                    logging.warning(f"日期 {depart_date} - {return_date} 没有找到航班")

            except Exception as e:
                logging.error(f"爬取日期 {config['booking']['booking_search_condition']['depart']} - "
                              f"{config['booking']['booking_search_condition']['return']} 时出错: {e}")

        # 按价格排序
        self._results.sort(key=lambda x: x["price"]["total"] if x["price"] else float('inf'))

        return self._results

    def find_cheapest_flights(self, top_n: int = 5) -> List[Dict[str, Any]]:
        """
        找出最便宜的几个航班

        Args:
            top_n: 返回前几个最便宜的航班，默认为5个

        Returns:
            最便宜的几个航班信息
        """
        if not self._results:
            return []

        return self._results[:min(top_n, len(self._results))]

    def save_results_csv(self, filename: str = "multi_date_flights.csv") -> str:
        """
        Save results to a CSV file

        Args:
            filename: 文件的默认名，默认为 "multi_date_flights.csv"

        Returns:
            str: 保存的文件路径
        """
        if not self._results:
            logging.warning("No results to save")
            return ""

        try:

            # Get filename from existing path
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
            output_dir = os.path.join(project_root, "output")
            os.makedirs(output_dir, exist_ok=True)
            filepath = os.path.join(output_dir, filename)

            import csv

            # Define CSV fields
            fieldnames = [
                "departure_date", "return_date", "price", "currency",
                "origin", "destination", "outbound_departure_time", "outbound_arrival_time",
                "outbound_flight_time", "outbound_transit", "airline",
                "inbound_departure_time", "inbound_arrival_time", "inbound_flight_time",
                "inbound_transit", "inbound_airline", "personal_item",
                "cabin_baggage", "checked_baggage", "booking_link"
            ]

            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for flight in self._results:
                    # Prepare row data
                    row = {
                        "departure_date": flight["depart_date"],
                        "return_date": flight["return_date"],
                        "price": flight["price"]["total"] if flight["price"] else "",
                        "currency": flight["price"]["currency"] if flight["price"] else "",
                        "origin": flight["airport"]["outbound"]["departure"] if flight["airport"] else "",
                        "destination": flight["airport"]["outbound"]["arrival"] if flight["airport"] else "",
                        "airline": flight["airline"]["outbound"]["main_carrier"]["name"] if flight[
                                                                                                "airline"] and "main_carrier" in
                                                                                            flight["airline"][
                                                                                                "outbound"] else "",
                    }

                    # Process outbound information
                    if flight["time"] and "outbound" in flight["time"]:
                        row["outbound_departure_time"] = flight["time"]["outbound"]["departure_time"].replace("T",
                                                                                                              " ") if "departure_time" in \
                                                                                                                      flight[
                                                                                                                          "time"][
                                                                                                                          "outbound"] else ""
                        row["outbound_arrival_time"] = flight["time"]["outbound"]["arrival_time"].replace("T",
                                                                                                          " ") if "arrival_time" in \
                                                                                                                  flight[
                                                                                                                      "time"][
                                                                                                                      "outbound"] else ""
                        row["outbound_flight_time"] = flight["time"]["outbound"][
                            "total_time_formatted"] if "total_time_formatted" in flight["time"]["outbound"] else ""

                    # Process outbound transit
                    if flight["airport"] and "outbound" in flight["airport"] and "transit" in flight["airport"][
                        "outbound"] and flight["airport"]["outbound"]["transit"]:
                        transit_airports = []
                        for airport in flight["airport"]["outbound"]["transit"]:
                            transit_airports.append(airport)
                        row["outbound_transit"] = " → ".join(transit_airports)
                    else:
                        row["outbound_transit"] = "Direct"

                    # Process inbound information
                    if flight["time"] and "inbound" in flight["time"]:
                        row["inbound_departure_time"] = flight["time"]["inbound"]["departure_time"].replace("T",
                                                                                                            " ") if "departure_time" in \
                                                                                                                    flight[
                                                                                                                        "time"][
                                                                                                                        "inbound"] else ""
                        row["inbound_arrival_time"] = flight["time"]["inbound"]["arrival_time"].replace("T",
                                                                                                        " ") if "arrival_time" in \
                                                                                                                flight[
                                                                                                                    "time"][
                                                                                                                    "inbound"] else ""
                        row["inbound_flight_time"] = flight["time"]["inbound"][
                            "total_time_formatted"] if "total_time_formatted" in flight["time"]["inbound"] else ""

                    # Process inbound transit
                    if flight["airport"] and "inbound" in flight["airport"] and "transit" in flight["airport"][
                        "inbound"] and flight["airport"]["inbound"]["transit"]:
                        transit_airports = []
                        for airport in flight["airport"]["inbound"]["transit"]:
                            transit_airports.append(airport)
                        row["inbound_transit"] = " → ".join(transit_airports)
                    else:
                        row["inbound_transit"] = "Direct"

                    # Process inbound airline
                    if flight["airline"] and "inbound" in flight["airline"] and "main_carrier" in flight["airline"][
                        "inbound"]:
                        row["inbound_airline"] = flight["airline"]["inbound"]["main_carrier"]["name"]

                    # Process baggage information
                    if flight["luggage"]:
                        row["personal_item"] = flight["luggage"].get("personal", "")
                        row["cabin_baggage"] = flight["luggage"].get("cabin", "")
                        row["checked_baggage"] = flight["luggage"].get("checked", "")

                    # Process booking link
                    row["booking_link"] = flight["booking_link"] if flight["booking_link"] else ""

                    # Write row
                    writer.writerow(row)

            logging.info(f"Results saved to CSV: {filepath}")
            return filepath
        except Exception as e:
            logging.error(f"Error saving CSV: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return ""

    def run(self, start_date: str, days_range: int = 10, return_days: int = 36, top_n: int = 5) -> str:
        """
        运行多日期爬虫

        Args:
            start_date: 开始日期，格式为 YYYY-MM-DD
            days_range: 出发日期范围天数，默认为10天
            return_days: 返程天数，默认为36天
            top_n: 显示前几个最便宜的航班，默认为5个

        Returns:
            格式化后的结果文本
        """
        # 生成日期范围
        date_pairs = self.generate_date_range(start_date, days_range, return_days)
        logging.info(f"生成了 {len(date_pairs)} 个日期组合")

        # 准备配置
        self.prepare_date_configs(date_pairs)

        # 爬取所有日期
        self.scrape_all_dates()

        # 保存结果
        # self.save_results_csv()
        logging.info("已保存到{}目录".format(os.path.join(project_root, "output")))
        return self.save_results_csv()


if __name__ == "__main__":
    # 设置日志
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # 示例用法
    scraper = MultiDateBookingScraper(ScraperFactory.create_scraper("booking_multi_date"))
    result = scraper.run("2025-07-01", days_range=5, return_days=36, top_n=5)
    print(result)
