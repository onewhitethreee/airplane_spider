# flight_scraper/core/data/data_processor.py
from flight_scraper.core.data.data_models import FlightOffer, SegmentInfo


class FlightDataProcessor:
    """处理航班数据的类"""

    def __init__(self, raw_data):
        """
        初始化数据处理器

        Args:
            raw_data: 原始航班数据
        """
        self.raw_data = raw_data
        self.processed_offers = []

    def process(self):
        """
        处理原始数据，转换为结构化的FlightOffer对象

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
                print(f"处理航班 {i} 时出错: {e}")
                continue

        return self.processed_offers

    def _extract_price(self, offer):
        """提取价格信息"""
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
        """提取航段信息"""
        # 这里实现提取航段详细信息的逻辑
        # 返回SegmentInfo对象
        pass

    def _extract_luggage(self, offer):
        """提取行李信息"""
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
        """生成预订链接"""
        # 实现链接生成逻辑
        return ""