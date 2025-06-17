# trip_processor.py
from flight_scraper.core.data.data_models import FlightOffer, SegmentInfo, LayoverInfo
from flight_scraper.core.data.data_formatter import format_time_duration, parse_iso_time
import logging

from flight_scraper.core.data.processor.data_processor import FlightDataProcessor


class TripDataProcessor(FlightDataProcessor):
    pass

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    processor = TripDataProcessor(None)
    processor.process()