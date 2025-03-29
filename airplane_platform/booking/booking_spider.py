# booking_spider.py
from datetime import datetime
import logging
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
        # 请求头
        self._headers = self._initialize_headers()
        # 包含着所有json的信息
        self._fight_json_info = None
        # 包含着在flightOffers下的所有信息
        self._fightOffers_info = None

        # 是否已经加载过数据
        self._data_loaded = False

    def load_data(self) -> bool:
        """加载并解析数据，确保只执行一次"""
        if not self._data_loaded:
            self.parse_flights()
            if self._fight_json_info:
                self._fightOffers_info = self._fight_json_info.get("flightOffers")
                if self._fightOffers_info is None:
                    logging.error("flightOffers信息为空")
                self._data_loaded = True
            return True
        return self._data_loaded

    def _initialize_headers(self):
        """初始化headers需要的信息"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        }
        return headers

    def _initialize_proxies(self):
        """初始化proxies需要的信息. 暂时搁置. 有一个self._proxies属性，里面有x个代理信息。 用来防止IP被ban"""
        self._proxies = None  # 暂时搁置

    def get_flight_info(self) -> None:
        """获取航班信息，通过requests获取到json信息，写入flights.json文件"""
        url = self.booking_api_url
        params = self.booking_search_condition
        response = requests.get(
            url,
            params=params,
            headers=self._headers,
            proxies=self._proxies,
            verify=False,
        )
        with open("flights.json", "w", encoding="utf-8") as f:
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
        """重写__str__方法，显示所有航班信息及预订链接"""
        if not self.load_data() or not self._fightOffers_info:
            return "数据未加载，无法显示航班信息"

        try:
            all_info = []

            # 获取航班数量
            flights_count = len(self._fightOffers_info)
            all_info.append(f"=== 共找到 {flights_count} 个航班方案 ===\n")

            # 遍历所有航班
            for page in range(flights_count):
                all_info.append(f"\n====== 航班方案 {page+1}/{flights_count} ======")

                # 获取价格信息
                price_info = self.parse_price(page)
                if price_info:
                    all_info.append(f"价格: {price_info['total']} {price_info['currency']}")

                # 获取航空公司信息
                airline_info = self.parse_airline(page)
                if airline_info:
                    outbound_carrier = airline_info['outbound']['main_carrier']
                    inbound_carrier = airline_info['inbound']['main_carrier']
                    all_info.append(f"主要承运商: {outbound_carrier.get('name', '')} ({outbound_carrier.get('code', '')})")
                    
                    # 如果往返的主要承运商不同，则显示
                    if outbound_carrier.get('code') != inbound_carrier.get('code'):
                        all_info.append(f"返程承运商: {inbound_carrier.get('name', '')} ({inbound_carrier.get('code', '')})")

                # 获取机场和时间信息的简洁版本
                airport_info = self.parse_airport(page)
                time_info = self.parse_time(page)
                
                if airport_info and time_info:
                    # 去程信息
                    out_dep_time = time_info['outbound']['departure_time'].replace('T', ' ')
                    out_arr_time = time_info['outbound']['arrival_time'].replace('T', ' ')
                    
                    all_info.append("\n-- 去程 --")
                    all_info.append(f"{out_dep_time} {airport_info['outbound']['departure']} → {out_arr_time} {airport_info['outbound']['arrival']}")
                    all_info.append(f"飞行时间: {time_info['outbound']['total_time_formatted']}")
                    
                    # 去程中转信息
                    if airport_info['outbound']['transit']:
                        transit_info = []
                        for i, airport in enumerate(airport_info['outbound']['transit']):
                            layover_time = time_info['outbound']['layovers'][i]['layover_time_formatted'] if time_info['outbound']['layovers'] else "未知"
                            transit_info.append(f"{airport} (停留 {layover_time})")
                        all_info.append(f"中转: {' → '.join(transit_info)}")
                    
                    # 返程信息
                    in_dep_time = time_info['inbound']['departure_time'].replace('T', ' ')
                    in_arr_time = time_info['inbound']['arrival_time'].replace('T', ' ')
                    
                    all_info.append("\n-- 返程 --")
                    all_info.append(f"{in_dep_time} {airport_info['inbound']['departure']} → {in_arr_time} {airport_info['inbound']['arrival']}")
                    all_info.append(f"飞行时间: {time_info['inbound']['total_time_formatted']}")
                    
                    # 返程中转信息
                    if airport_info['inbound']['transit']:
                        transit_info = []
                        for i, airport in enumerate(airport_info['inbound']['transit']):
                            layover_time = time_info['inbound']['layovers'][i]['layover_time_formatted'] if time_info['inbound']['layovers'] else "未知"
                            transit_info.append(f"{airport} (停留 {layover_time})")
                        all_info.append(f"中转: {' → '.join(transit_info)}")

                # 获取行李额信息
                luggage_info = self.parse_luggage_allowance(page)
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

                # 生成预订链接
                booking_link = self.generate_booking_link(page)
                if booking_link:
                    all_info.append(f"\n预订链接: {booking_link}")

                # 添加分隔线
                if page < flights_count - 1:
                    all_info.append("\n" + "-" * 80)

            return "\n".join(all_info)

        except Exception as e:
            return f"获取航班信息时出错: {e}"

    def parse_flights(self) -> None:
        """解析flights.json文件"""
        if os.path.exists("flights.json"):
            with open("flights.json", "r", encoding="utf-8") as f:
                self._fight_json_info = json.load(f)
        else:
            logging.error("flights.json文件不存在")
            # 可以选择在这里自动尝试获取数据
            self.get_flight_info()
            # 再次尝试读取
            if os.path.exists("flights.json"):
                with open("flights.json", "r", encoding="utf-8") as f:
                    self._fight_json_info = json.load(f)

    def parse_flightOffers(self) -> dict:
        """在名为flightOffers的key下包含着第一页的所有航班信息"""
        self.load_data()

        return self._fightOffers_info

    def parse_price(self, page=0) -> dict:
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
        if not self.load_data() or not self._fightOffers_info:
            logging.error("数据未加载, 可能是因为没有获取到flight.json文件")
            return None

        try:
            price_units = self._fightOffers_info[page]["priceBreakdown"]["total"]["units"]
            price_nano = self._fightOffers_info[page]["priceBreakdown"]["total"]["nanos"]
            price_total = price_units + price_nano / 1000000000

            # 获取货币单位(如果有的话)
            currency = self._fightOffers_info[page]["priceBreakdown"].get("currencyCode", "EUR")

            # 返回字典格式
            price_info = {
                "total": price_total,
                "currency": currency,
                "units": price_units,
                "nanos": price_nano
            }

            return price_info
        except (IndexError, KeyError) as e:
            logging.error(f"解析价格失败: {e}")
            return None

    def _parse_iso_time(self, time_str) -> datetime:
        """手动解析ISO格式时间字符串"""
        # 处理格式如：2025-07-14T10:15:00
        date_part, time_part = time_str.split('T')
        year, month, day = map(int, date_part.split('-'))
        hour, minute, second = map(int, time_part.split(':'))
        return datetime(year, month, day, hour, minute, second)

    def parse_time(self, pages=0) -> dict:
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
        if not self.load_data() or not self._fightOffers_info:
            logging.error("数据未加载, 可能是因为没有获取到flight.json文件")
            return None
        try:
            segments = self._fightOffers_info[pages]["segments"]

            # 创建存储飞行时间信息的字典
            time_info = {
                "outbound": {
                    "departure_time": segments[0]["departureTime"],
                    "arrival_time": segments[0]["arrivalTime"],
                    "total_time_seconds": segments[0]["totalTime"],
                    "total_time_formatted": self._format_time_duration(segments[0]["totalTime"]),
                    "layovers": []
                },
                "inbound": {
                    "departure_time": segments[1]["departureTime"],
                    "arrival_time": segments[1]["arrivalTime"],
                    "total_time_seconds": segments[1]["totalTime"],
                    "total_time_formatted": self._format_time_duration(segments[1]["totalTime"]),
                    "layovers": []
                }
            }

            # 计算去程中转停留时间
            if len(segments[0]["legs"]) > 1:
                for i in range(len(segments[0]["legs"]) - 1):
                    current_leg_arrival = segments[0]["legs"][i]["arrivalTime"]
                    next_leg_departure = segments[0]["legs"][i+1]["departureTime"]

                    # 将时间字符串转换为datetime对象
                    arrival_time = self._parse_iso_time(current_leg_arrival)
                    departure_time = self._parse_iso_time(next_leg_departure)

                    # 计算停留时间（秒）
                    layover_seconds = (departure_time - arrival_time).total_seconds()

                    layover_info = {
                        "airport": segments[0]["legs"][i]["arrivalAirport"]["name"],
                        "layover_time_seconds": int(layover_seconds),
                        "layover_time_formatted": self._format_time_duration(int(layover_seconds))
                    }
                    time_info["outbound"]["layovers"].append(layover_info)

            # 计算返程中转停留时间
            if len(segments[1]["legs"]) > 1:
                for i in range(len(segments[1]["legs"]) - 1):
                    current_leg_arrival = segments[1]["legs"][i]["arrivalTime"]
                    next_leg_departure = segments[1]["legs"][i+1]["departureTime"]

                    # 将时间字符串转换为datetime对象
                    arrival_time = datetime.fromisoformat(current_leg_arrival)
                    departure_time = datetime.fromisoformat(next_leg_departure)

                    # 计算停留时间（秒）
                    layover_seconds = (departure_time - arrival_time).total_seconds()

                    layover_info = {
                        "airport": segments[1]["legs"][i]["arrivalAirport"]["name"],
                        "layover_time_seconds": int(layover_seconds),
                        "layover_time_formatted": self._format_time_duration(int(layover_seconds))
                    }
                    time_info["inbound"]["layovers"].append(layover_info)

            return time_info

        except (IndexError, KeyError) as e:
            logging.error(f"解析飞行时间失败: {e}")
            return None

    def _format_time_duration(self, seconds) -> str:
        """将秒数格式化为小时和分钟"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"

    def parse_airport(self, pages=0) -> dict:
        """
        解析机场，获取去程和返程的中转机场
        
        返回一个字典，包含了去程和返程的机场信息
        其格式为：
        {
            'outbound': {
                'departure': '出发机场',
                'arrival': '到达机场',
                'transit': ['中转机场1', '中转机场2']
            },
            'inbound': {
                'departure': '出发机场',
                'arrival': '到达机场',
                'transit': ['中转机场1', '中转机场2']
            }
        }
        """
        if not self.load_data() or not self._fightOffers_info:
            logging.error("数据未加载, 可能是因为没有获取到flight.json文件")
            return None
        try:
            segments = self._fightOffers_info[pages]["segments"]

            # 存储结果的字典
            airports = {
                "outbound": {
                    "departure": segments[0]["departureAirport"]["name"],
                    "arrival": segments[0]["arrivalAirport"]["name"],
                    "transit": []
                },
                "inbound": {
                    "departure": segments[1]["departureAirport"]["name"],
                    "arrival": segments[1]["arrivalAirport"]["name"],
                    "transit": []
                }
            }

            # 提取去程的中转机场
            if len(segments[0]["legs"]) > 1:
                for i in range(1, len(segments[0]["legs"])):
                    # 中转机场是前一个leg的到达机场
                    transit_airport = segments[0]["legs"][i-1]["arrivalAirport"]["name"]
                    airports["outbound"]["transit"].append(transit_airport)

            # 提取返程的中转机场
            if len(segments[1]["legs"]) > 1:
                for i in range(1, len(segments[1]["legs"])):
                    transit_airport = segments[1]["legs"][i-1]["arrivalAirport"]["name"]
                    airports["inbound"]["transit"].append(transit_airport)
            return airports

        except (IndexError, KeyError) as e:
            logging.error(f"解析机场失败: {e}")
            return None

    def parse_airline(self, pages=0) -> dict:
        """
        解析航空公司信息
        
        返回一个字典，包含了去程和返程的航空公司信息
        其格式为：
        {
            'outbound': {
                'main_carrier': {'name': '航空公司名称', 'code': '航空公司代码', 'logo': '航空公司logo'},
                'leg_carriers': [
                    {'name': '段1航空公司名称', 'code': '段1航空公司代码', 'logo': '段1航空公司logo'},
                    {'name': '段2航空公司名称', 'code': '段2航空公司代码', 'logo': '段2航空公司logo'},
                    ...
                ]
            },
            'inbound': {
                'main_carrier': {'name': '航空公司名称', 'code': '航空公司代码', 'logo': '航空公司logo'},
                'leg_carriers': [
                    {'name': '段1航空公司名称', 'code': '段1航空公司代码', 'logo': '段1航空公司logo'},
                    {'name': '段2航空公司名称', 'code': '段2航空公司代码', 'logo': '段2航空公司logo'},
                    ...
                ]
            }
        }
        """
        if not self.load_data() or not self._fightOffers_info:
            logging.error("数据未加载, 可能是因为没有获取到flight.json文件")
            return None
        try:
            segments = self._fightOffers_info[pages]["segments"]

            # 存储结果的字典
            airlines = {
                "outbound": {
                    "main_carrier": {},
                    "leg_carriers": []
                },
                "inbound": {
                    "main_carrier": {},
                    "leg_carriers": []
                }
            }

            # 处理去程航空公司信息
            outbound_legs = segments[0]["legs"]
            # 设置主要承运商为第一段的承运商
            if outbound_legs and "carriersData" in outbound_legs[0] and outbound_legs[0]["carriersData"]:
                main_carrier = outbound_legs[0]["carriersData"][0]
                airlines["outbound"]["main_carrier"] = {
                    "name": main_carrier.get("name", ""),
                    "code": main_carrier.get("code", ""),
                    "logo": main_carrier.get("logo", "")
                }

            # 处理每一段的承运商
            for leg in outbound_legs:
                if "carriersData" in leg and leg["carriersData"]:
                    carrier = leg["carriersData"][0]  # 通常取第一个承运商
                    airlines["outbound"]["leg_carriers"].append({
                        "name": carrier.get("name", ""),
                        "code": carrier.get("code", ""),
                        "logo": carrier.get("logo", "")
                    })

            # 处理返程航空公司信息
            inbound_legs = segments[1]["legs"]
            # 设置主要承运商为第一段的承运商
            if inbound_legs and "carriersData" in inbound_legs[0] and inbound_legs[0]["carriersData"]:
                main_carrier = inbound_legs[0]["carriersData"][0]
                airlines["inbound"]["main_carrier"] = {
                    "name": main_carrier.get("name", ""),
                    "code": main_carrier.get("code", ""),
                    "logo": main_carrier.get("logo", "")
                }

            # 处理每一段的承运商
            for leg in inbound_legs:
                if "carriersData" in leg and leg["carriersData"]:
                    carrier = leg["carriersData"][0]  # 通常取第一个承运商
                    airlines["inbound"]["leg_carriers"].append({
                        "name": carrier.get("name", ""),
                        "code": carrier.get("code", ""),
                        "logo": carrier.get("logo", "")
                    })

            return airlines

        except (IndexError, KeyError) as e:
            logging.error(f"解析航空公司失败: {e}")
            return None

    def parse_luggage_allowance(self, pages=0) -> dict:
        """
        解析行李额
        
        返回一个字典，包含了随身小包，随身行李和托运行李的信息
        其格式为：
        {
            'personal': '1个小包',
            'cabin': '1个行李',
            'checked': '1个行李'
        }
        """
        if not self.load_data() or not self._fightOffers_info:
            logging.error("数据未加载, 可能是因为没有获取到flight.json文件")
            return None
        try:
            luggage_allowance = self._fightOffers_info[pages]["brandedFareInfo"]["features"]

            # 创建一个字典来存储行李类别信息
            luggage_info = {
                'personal': None,  # 随身小包
                'cabin': None,     # 随身行李
                'checked': None    # 托运行李
            }

            for luggage in luggage_allowance:
                if "label" in luggage and "featureName" in luggage:
                    feature_name = luggage.get("featureName")
                    label = luggage.get("label")

                    if feature_name == "PERSONAL_BAGGAGE":
                        luggage_info['personal'] = label
                    elif feature_name == "CABIN_BAGGAGE":
                        luggage_info['cabin'] = label
                    elif feature_name == "CHECK_BAGGAGE":
                        luggage_info['checked'] = label

            return luggage_info

        except (IndexError, KeyError) as e:
            logging.error(f"解析行李额失败: {e}")
            return None

    def parse_link(self, pages=0) -> dict:
        """
        解析航班链接token
        
        返回一个字典，包含token信息
        其格式为：
        {
            'token': '链接token'
        }
        """
        if not self.load_data() or not self._fightOffers_info:
            logging.error("数据未加载, 可能是因为没有获取到flight.json文件")
            return None
        try:
            # 获取指定页码的航班信息
            flight_offer = self._fightOffers_info[pages]

            # 初始化结果字典
            link_info = {}

            # 检查token是否存在
            if "token" in flight_offer:
                token = flight_offer["token"]
                link_info["token"] = token
            else:
                logging.warning(f"在航班 {pages} 中未找到token信息")

            return link_info

        except (IndexError, KeyError) as e:
            logging.error(f"解析链接失败: {e}")
            return None


    def generate_booking_link(self, pages=0) -> str:
        """
        根据航班信息生成booking.com预订链接

        Args:
            pages: 航班索引，默认为0

        Returns:
            生成的booking.com预订链接
        """
        if not self.load_data() or not self._fightOffers_info:
            logging.error("数据未加载, 可能是因为没有获取到flight.json文件")
            return None

        try:
            # 获取token
            link_info = self.parse_link(pages)
            if not link_info or "token" not in link_info:
                logging.error("无法获取token信息")
                return None

            token = link_info["token"]

            # 获取机场信息
            airport_info = self.parse_airport(pages)
            if not airport_info:
                logging.error("无法获取机场信息")
                return None

            # 获取出发/返回机场代码
            from_airport = airport_info["outbound"]["departure"].split(" ")[0]
            to_airport = airport_info["outbound"]["arrival"].split(" ")[0]

            # 获取机场所在城市代码
            from_city = segments = self._fightOffers_info[pages]["segments"][0][
                "departureAirport"
            ]["city"]
            to_city = segments = self._fightOffers_info[pages]["segments"][0][
                "arrivalAirport"
            ]["city"]

            # 获取国家代码
            from_country = segments = self._fightOffers_info[pages]["segments"][0][
                "departureAirport"
            ]["country"]
            to_country = segments = self._fightOffers_info[pages]["segments"][0][
                "arrivalAirport"
            ]["country"]

            # 获取机场名称（需要URL编码）
            from_location_name = self._url_encode(
                self._fightOffers_info[pages]["segments"][0]["departureAirport"]["name"]
            )
            to_location_name = self._url_encode(
                self._fightOffers_info[pages]["segments"][0]["arrivalAirport"]["cityName"]
            )

            # 获取出发和返回日期
            time_info = self.parse_time(pages)
            if not time_info:
                logging.error("无法获取时间信息")
                return None

            depart_date = time_info["outbound"]["departure_time"].split("T")[0]
            return_date = time_info["inbound"]["departure_time"].split("T")[0]

            # 构建基本URL
            base_url = "https://flights.booking.com/flights/"

            # 构建路径部分
            path = f"{from_airport}.AIRPORT-{to_city}.CITY/{token}/"

            # 构建查询参数
            query_params = {
                "type": "ROUNDTRIP",
                "adults": "1",
                "cabinClass": "ECONOMY",
                "children": "",
                "from": f"{from_airport}.AIRPORT",
                "to": f"{to_city}.CITY",
                "depart": depart_date,
                "return": return_date,
            }

            # 构建查询字符串
            query_string = "&".join([f"{k}={v}" for k, v in query_params.items()])

            # 拼接完整URL
            full_url = f"{base_url}{path}?{query_string}"

            return full_url

        except (IndexError, KeyError) as e:
            logging.error(f"生成链接失败: {e}")
            return None


    def _url_encode(self, text):
        """将文本进行URL编码"""
        import urllib.parse

        return urllib.parse.quote(text)


# if __name__ == "__main__":
#     config_manager = ConfigManager()
#     json_config = config_manager.register_parser(
#         r"config/configs/config_booking.json", JsonParse
#     )
#     booking_spider = Booking_spider(json_config)
#     # booking_spider.get_flight_info()
#     # booking_spider.parse_airport()
#     # print(booking_spider.generate_booking_link())
#     with open("flights_info.txt", "w", encoding="utf-8") as f:
#         f.write(str(booking_spider))
