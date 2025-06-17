from flight_scraper.core.data.data_models import FlightOffer, SegmentInfo, LayoverInfo
from flight_scraper.core.data.data_formatter import format_time_duration, parse_iso_time
import logging

from flight_scraper.core.data.processor.data_processor import FlightDataProcessor

class LyDataProcessor(FlightDataProcessor):
    def process(self):
        pass
    def _extract_segment(self, segment):
        pass
    def _extract_luggage(self, offer):
        pass
    def _extract_price(self, offer):
        pass
    def _extract_layover(self, offer):
        pass
    def _generate_booking_link(self, offer, outbound, inbound):
        pass

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    processor = LyDataProcessor(None)
    processor.process()