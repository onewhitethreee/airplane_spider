# scraper.py
import logging
import os
import sys
import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# 获取项目根目录路径
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.append(project_root)

from flight_scraper.core.data.processor.processor_factory import DataProcessorFactory
from flight_scraper.core.factory.factory import ScraperFactory
from flight_scraper.core.abstract.abstract_methods import FlightScraper


def rm_flights_json():
    """删除flights.json文件"""
    if os.path.exists(r"flights.json"):
        os.remove(r"flights.json")


def _url_encode(text):
    """将文本进行URL编码"""
    import urllib.parse

    return urllib.parse.quote(text)


class BookingScraper(FlightScraper):

    def __init__(self, platform_config):

        self._platform_config = platform_config
        super().__init__(platform_config)

        self._data_loaded = False
        self._raw_data = None
        self._processed_offers = []

        import uuid
        self._save_file_path = f"flights_{uuid.uuid4().hex}.json" # 修复多日期搜索时文件名冲突的问题
        self._platform_type = "booking"

    def load_data(self) -> bool:
        """加载并解析数据，确保只执行一次"""
        if self._data_loaded:
            return True

        self.parse_flights()
        if not self._raw_data:
            return False

        processor = DataProcessorFactory.create_processor(self._platform_type, self._raw_data)
        self._processed_offers = processor.process()
        self._data_loaded = True
        return True

    def _initialize_headers(self):
        """初始化headers需要的信息"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        }
        return headers

    def _initialize_proxies(self):
        """初始化proxies需要的信息. 暂时搁置. 有一个self._proxies属性，里面有x个代理信息。 用来防止IP被ban"""
        return self._platform_config.get_proxies_config()

    def requests_flight_info(self) -> None:
        """
        获取航班信息，通过requests获取到json信息，写入flights.json文件
        """
        url = self._platform_config.get_api_url()
        params = self._platform_config.get_search_params()
        try:

            response = requests.get(
                url,
                params=params,
                headers=self._headers,
                proxies=self._proxies,
                verify=False,
            )

            response.raise_for_status()  # 检查请求是否成功

            with open(self._save_file_path, "w", encoding="utf-8") as f:
                f.write(response.text)
                current_dir = os.path.dirname(os.path.abspath(__file__))

                logging.debug(f"航班信息已保存到 {self._save_file_path}")
        except requests.RequestException as e:
            logging.error(f"请求航班信息失败: {e}")
            return None

    def parse_flights(self) -> None:
        """解析flights.json文件"""
        if not os.path.exists(self._save_file_path):
            logging.error(f"{self._save_file_path}文件不存在")
            logging.info("重新请求航班信息")
            self.requests_flight_info()

        if os.path.exists(self._save_file_path):
            with open(self._save_file_path, "r", encoding="utf-8") as f:
                self._raw_data = json.load(f)
        else:
            logging.error(f"无法加载航班数据文件")



    def parse_price(self, index=0):
        """
        解析价格

        返回一个字典，包含了总价格，货币单位，单位和纳秒
        其格式为：
        {
            'total': 0.0,
            'currency': 'EUR',
            'units': 0,
            'nanos': 0
        }
        """
        if not self.load_data() or index >= len(self._processed_offers):
            logging.error("数据未加载或索引超出范围")
            return None
        return self._processed_offers[index].price

    def parse_time(self, index=0):
        """
        解析飞行时间， 包括去程和返程的飞行时间，中转时间

        返回一个字典，包含了去程和返程的飞行时间信息
        其格式为：
        "outbound": {
                    "departure_time": 出发时间,
                    "arrival_time": 到达时间,
                    "total_time_seconds": 总飞行时间（秒）,
                    "total_time_formatted": 格式化后的飞行时间,
                    "layovers": [] # 中转信息
                },
        "inbound": {
                    "departure_time": 出发时间,
                    "arrival_time": 到达时间,
                    "total_time_seconds": 总飞行时间（秒）,
                    "total_time_formatted": 格式化后的飞行时间,
                    "layovers": []
        }

        """
        if not self.load_data() or index >= len(self._processed_offers):
            logging.error("数据未加载或索引超出范围")
            return None
        return {
            "outbound": self._processed_offers[index].outbound.time_info,
            "inbound": self._processed_offers[index].inbound.time_info
        }

    def parse_airport(self, index=0):
        """兼容抽象类的接口，实际调用已处理的数据"""
        if not self.load_data() or index >= len(self._processed_offers):
            return None

        flight = self._processed_offers[index]
        return {
            "outbound": {
                "departure": flight.outbound.departure,
                "arrival": flight.outbound.arrival,
                "transit": flight.outbound.transit
            },
            "inbound": {
                "departure": flight.inbound.departure,
                "arrival": flight.inbound.arrival,
                "transit": flight.inbound.transit
            }
        }

    def parse_airline(self, index=0):
        """兼容抽象类的接口，实际调用已处理的数据"""
        if not self.load_data() or index >= len(self._processed_offers):
            return None

        flight = self._processed_offers[index]
        return {
            "outbound": {
                "main_carrier": flight.outbound.main_carrier,
                "leg_carriers": flight.outbound.leg_carriers
            },
            "inbound": {
                "main_carrier": flight.inbound.main_carrier,
                "leg_carriers": flight.inbound.leg_carriers
            }
        }

    def parse_luggage_allowance(self, index=0):
        """兼容抽象类的接口，实际调用已处理的数据"""
        if not self.load_data() or index >= len(self._processed_offers):
            return None
        return self._processed_offers[index].luggage

    def parse_link(self, index=0):
        """
        解析航班链接token

        返回一个字典，包含token信息
        其格式为：
        {
            'token': '链接token'
        }
        """
        if not self.load_data() or not self._processed_offers:
            logging.error("数据未加载, 可能是因为没有获取到flight.json文件")
            return None
        try:
            # 获取指定页码的航班信息
            flight_offer = self._processed_offers[index]

            # 初始化结果字典
            link_info = {}

            # 检查token是否存在
            if "token" in flight_offer:
                token = flight_offer["token"]
                link_info["token"] = token
            else:
                logging.warning(f"在航班 {index} 中未找到token信息")

            return link_info

        except (IndexError, KeyError) as e:
            logging.error(f"解析链接失败: {e}")
            return None

    def generate_booking_link(self, index=0):
        """兼容抽象类的接口，实际调用已处理的数据"""
        if not self.load_data() or index >= len(self._processed_offers):
            return None
        return self._processed_offers[index].booking_link

    def run(self):
        """运行爬虫流程"""
        self.requests_flight_info()
        if not self.load_data():
            return "获取航班数据失败"
        return self.format_result()

    def format_result(self):
        """显示所有航班信息及预订链接"""
        if not self._data_loaded:
            logging.error("数据未加载，请先运行run方法")
            return "数据未加载，请先运行run方法"
        if not self._processed_offers:
            logging.error("没有航班数据")
            return "没有航班数据"

        try:
            all_info = []

            # 获取航班数量
            flights_count = len(self._processed_offers)
            all_info.append(f"=== 共找到 {flights_count} 个航班方案 ===\n")

            # 遍历所有航班
            for index, flight in enumerate(self._processed_offers):
                all_info.append(f"\n====== 航班方案 {index + 1}/{flights_count} ======")

                # 获取价格信息
                price_info = flight.price
                if price_info:
                    all_info.append(f"价格: {price_info['total']} {price_info['currency']}")

                # 获取航空公司信息
                outbound_carrier = flight.outbound.main_carrier
                inbound_carrier = flight.inbound.main_carrier
                all_info.append(
                    f"主要承运商: {outbound_carrier.get('name', '')} ({outbound_carrier.get('code', '')})")

                # 如果往返的主要承运商不同，则显示
                if outbound_carrier.get('code') != inbound_carrier.get('code'):
                    all_info.append(
                        f"返程承运商: {inbound_carrier.get('name', '')} ({inbound_carrier.get('code', '')})")

                # 去程信息
                out_dep_time = flight.outbound.time_info["departure_time"].replace('T', ' ')
                out_arr_time = flight.outbound.time_info["arrival_time"].replace('T', ' ')

                all_info.append("\n-- 去程 --")
                all_info.append(
                    f"{out_dep_time} {flight.outbound.departure} → {out_arr_time} {flight.outbound.arrival}")
                all_info.append(f"飞行时间: {flight.outbound.time_info['total_time_formatted']}")

                # 去程中转信息
                if flight.outbound.transit:
                    transit_info = []
                    for i, airport in enumerate(flight.outbound.transit):
                        layover_time = flight.outbound.time_info['layovers'][i].layover_time_formatted
                        transit_info.append(f"{airport} (停留 {layover_time})")
                    all_info.append(f"中转: {' → '.join(transit_info)}")

                # 返程信息
                in_dep_time = flight.inbound.time_info["departure_time"].replace('T', ' ')
                in_arr_time = flight.inbound.time_info["arrival_time"].replace('T', ' ')

                all_info.append("\n-- 返程 --")
                all_info.append(
                    f"{in_dep_time} {flight.inbound.departure} → {in_arr_time} {flight.inbound.arrival}")
                all_info.append(f"飞行时间: {flight.inbound.time_info['total_time_formatted']}")

                # 返程中转信息
                if flight.inbound.transit:
                    transit_info = []
                    for i, airport in enumerate(flight.inbound.transit):
                        layover_time = flight.inbound.time_info['layovers'][i].layover_time_formatted
                        transit_info.append(f"{airport} (停留 {layover_time})")
                    all_info.append(f"中转: {' → '.join(transit_info)}")

                # 获取行李额信息
                luggage_info = flight.luggage
                if luggage_info:
                    all_info.append("\n-- 行李额 --")
                    luggage_details = []
                    if luggage_info.get('personal'):
                        luggage_details.append(f"随身小包: {luggage_info['personal']}")
                    if luggage_info.get('cabin'):
                        luggage_details.append(f"随身行李: {luggage_info['cabin']}")
                    if luggage_info.get('checked'):
                        luggage_details.append(f"托运行李: {luggage_info['checked']}")
                    all_info.append(" | ".join(luggage_details))

                # 显示预订链接
                if flight.booking_link:
                    all_info.append(f"\n预订链接: {flight.booking_link}")

                # 添加分隔线
                if index < flights_count - 1:
                    all_info.append("\n" + "-" * 80)

            return "\n".join(all_info)

        except Exception as e:
            return f"获取航班信息时出错: {e}"

    def __del__(self):
        """析构函数，删除临时文件"""
        try:
            if hasattr(self, '_save_file_path') and os.path.exists(self._save_file_path):
                os.remove(self._save_file_path)
                logging.debug(f"临时文件已删除: {self._save_file_path}")
        except Exception as e:
            logging.warning(f"删除临时文件时出错: {e}")
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    scraper_config = ScraperFactory.create_scraper("booking")

    # 获取航班信息
    result = scraper_config.run()

    # print(result)
    print(result)