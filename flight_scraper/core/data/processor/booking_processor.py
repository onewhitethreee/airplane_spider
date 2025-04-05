# flight_scraper/core/data/platform_processors/booking_processor.py
from flight_scraper.core.data.data_models import FlightOffer, SegmentInfo, LayoverInfo
from flight_scraper.core.data.data_formatter import format_time_duration, parse_iso_time
import logging

from flight_scraper.core.data.processor.data_processor import FlightDataProcessor


class BookingDataProcessor(FlightDataProcessor):
    """处理Booking平台的航班数据"""

    def process(self):
        """
        处理Booking平台原始数据，转换为结构化的FlightOffer对象

        Returns:
            List[FlightOffer]: 处理后的航班列表
        """
        if not self.raw_data or "flightOffers" not in self.raw_data:
            return []

        flight_offers = self.raw_data["flightOffers"]

        for i, offer in enumerate(flight_offers):
            try:
                # 处理价格
                price_info = self._extract_price(offer)

                # 处理出发段
                outbound_segment = self._extract_segment(offer["segments"][0])

                # 处理返程段
                inbound_segment = self._extract_segment(offer["segments"][1])

                # 处理行李
                luggage_info = self._extract_luggage(offer)

                # 处理token
                token = offer.get("token", "")

                # 创建FlightOffer对象
                flight_offer = FlightOffer(
                    id=i,
                    price=price_info,
                    outbound=outbound_segment,
                    inbound=inbound_segment,
                    luggage=luggage_info,
                    token=token,
                    booking_link=self._generate_booking_link(offer, outbound_segment, inbound_segment)
                )

                self.processed_offers.append(flight_offer)

            except Exception as e:
                logging.error(f"处理航班 {i} 时出错: {e}")
                continue

        return self.processed_offers

    def _extract_price(self, offer):
        """提取价格信息 - Booking平台特定实现"""
        try:
            price_breakdown = offer.get("priceBreakdown", {})
            total = price_breakdown.get("total", {})
            units = total.get("units", 0)
            nanos = total.get("nanos", 0)
            price_total = units + nanos / 1000000000
            currency = price_breakdown.get("currencyCode", "EUR")

            return {
                "total": price_total,
                "currency": currency,
                "units": units,
                "nanos": nanos
            }
        except Exception:
            return {"total": 0, "currency": "EUR", "units": 0, "nanos": 0}

    def _extract_segment(self, segment):
        """提取航段信息 - Booking平台特定实现"""
        try:
            # 提取起始机场
            departure = segment["departureAirport"]["name"]
            arrival = segment["arrivalAirport"]["name"]

            # 提取中转机场
            transit_airports = []
            if len(segment["legs"]) > 1:
                for i in range(1, len(segment["legs"])):
                    transit_airport = segment["legs"][i - 1]["arrivalAirport"]["name"]
                    transit_airports.append(transit_airport)

            # 提取主要承运商
            main_carrier = {}
            if "legs" in segment and segment["legs"] and "carriersData" in segment["legs"][0]:
                carrier_data = segment["legs"][0]["carriersData"][0]
                main_carrier = {
                    "name": carrier_data.get("name", ""),
                    "code": carrier_data.get("code", ""),
                    "logo": carrier_data.get("logo", "")
                }

            # 提取各段承运商
            leg_carriers = []
            for leg in segment["legs"]:
                if "carriersData" in leg and leg["carriersData"]:
                    carrier = leg["carriersData"][0]
                    leg_carriers.append({
                        "name": carrier.get("name", ""),
                        "code": carrier.get("code", ""),
                        "logo": carrier.get("logo", "")
                    })

            # 提取时间信息
            time_info = {
                "departure_time": segment["departureTime"],
                "arrival_time": segment["arrivalTime"],
                "total_time_seconds": segment["totalTime"],
                "total_time_formatted": format_time_duration(segment["totalTime"]),
                "layovers": self._extract_layovers(segment)
            }

            # 创建SegmentInfo对象
            return SegmentInfo(
                departure=departure,
                arrival=arrival,
                transit=transit_airports,
                main_carrier=main_carrier,
                leg_carriers=leg_carriers,
                time_info=time_info
            )
        except Exception as e:
            logging.error(f"提取航段信息失败: {e}")
            return None

    def _extract_layovers(self, segment):
        """提取中转停留信息 - Booking平台特定实现"""
        layovers = []

        if len(segment["legs"]) > 1:
            for i in range(len(segment["legs"]) - 1):
                current_leg_arrival = segment["legs"][i]["arrivalTime"]
                next_leg_departure = segment["legs"][i + 1]["departureTime"]

                # 将时间字符串转换为datetime对象
                arrival_time = parse_iso_time(current_leg_arrival)
                departure_time = parse_iso_time(next_leg_departure)

                # 计算停留时间（秒）
                layover_seconds = (departure_time - arrival_time).total_seconds()

                layover_info = LayoverInfo(
                    airport=segment["legs"][i]["arrivalAirport"]["name"],
                    layover_time_seconds=int(layover_seconds),
                    layover_time_formatted=format_time_duration(int(layover_seconds))
                )
                layovers.append(layover_info)

        return layovers

    def _extract_luggage(self, offer):
        """提取行李信息 - Booking平台特定实现"""
        try:
            luggage_allowance = offer.get("brandedFareInfo", {}).get("features", [])

            luggage_info = {
                'personal': None,
                'cabin': None,
                'checked': None
            }

            for luggage in luggage_allowance:
                feature_name = luggage.get("featureName")
                label = luggage.get("label")

                if feature_name == "PERSONAL_BAGGAGE":
                    luggage_info['personal'] = label
                elif feature_name == "CABIN_BAGGAGE":
                    luggage_info['cabin'] = label
                elif feature_name == "CHECK_BAGGAGE":
                    luggage_info['checked'] = label

            return luggage_info
        except Exception:
            return {'personal': None, 'cabin': None, 'checked': None}

    def _generate_booking_link(self, offer, outbound, inbound):
        """生成预订链接 - Booking平台特定实现"""
        try:
            # 获取token
            token = offer.get("token", "")
            if not token:
                return ""

            # 获取出发/返回机场代码
            from_airport = offer["segments"][0]["departureAirport"]["code"]
            to_city = offer["segments"][0]["arrivalAirport"]["city"]

            # 获取出发和返回日期
            depart_date = offer["segments"][0]["departureTime"].split("T")[0]
            return_date = offer["segments"][1]["departureTime"].split("T")[0]

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
        except Exception as e:
            logging.error(f"生成预订链接失败: {e}")
            return ""