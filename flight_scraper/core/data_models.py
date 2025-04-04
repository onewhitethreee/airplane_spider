# core/data_models.py
from dataclasses import dataclass
from typing import List, Optional, Dict


@dataclass
class Airport:
    """
    机场信息类
    """
    name: str
    code: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None


@dataclass
class Carrier:
    """
    航空公司信息类
    """
    name: str
    code: Optional[str] = None
    logo: Optional[str] = None


@dataclass
class LayoverInfo:
    """
    中转信息类
    """
    airport: Airport
    layover_time_seconds: int
    layover_time_formatted: str


@dataclass
class TimeInfo:
    """
    航班时间信息类
    """
    departure_time: str
    arrival_time: str
    total_time_seconds: int
    total_time_formatted: str
    layovers: List[LayoverInfo]


@dataclass
class SegmentInfo:
    """
    航班段信息类
    """
    departure: Airport
    arrival: Airport
    transit: List[Airport]
    main_carrier: Carrier
    leg_carriers: List[Carrier]
    time_info: TimeInfo


@dataclass
class FlightOffer:
    """
    航班报价信息类
    """
    id: int
    price: Dict
    outbound: SegmentInfo
    inbound: SegmentInfo
    luggage: Dict
    token: str
    booking_link: str
