# flight_scraper/core/data/data_models.py
from dataclasses import dataclass
from typing import List, Optional, Dict

@dataclass
class Airport:
    name: str
    code: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    city_name: Optional[str] = None

@dataclass
class Carrier:
    name: str
    code: Optional[str] = None
    logo: Optional[str] = None

@dataclass
class LayoverInfo:
    airport: str
    layover_time_seconds: int
    layover_time_formatted: str

@dataclass
class TimeInfo:
    departure_time: str
    arrival_time: str
    total_time_seconds: int
    total_time_formatted: str
    layovers: List[LayoverInfo]

@dataclass
class SegmentInfo:
    departure: str
    arrival: str
    transit: List[str]
    main_carrier: Dict[str, str]
    leg_carriers: List[Dict[str, str]]
    time_info: Dict

@dataclass
class FlightOffer:
    id: int
    price: Dict
    outbound: SegmentInfo
    inbound: SegmentInfo
    luggage: Dict
    token: str
    booking_link: str