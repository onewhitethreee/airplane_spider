# 根据平台名称创建数据处理器
class DataProcessorFactory:

    @staticmethod
    def create_processor(platform_name, raw_data):
        """创建指定平台的数据处理器实例

        Args:
            platform_name: 平台名称
            raw_data: 原始数据

        Returns:
            FlightDataProcessor: 数据处理器实例
        """
        if platform_name.lower() == "booking":
            from flight_scraper.core.data.processor.booking_processor import BookingDataProcessor
            return BookingDataProcessor(raw_data)

        elif platform_name.lower() == "trip":
            from flight_scraper.core.data.processor.trip_processor import TripDataProcessor
            return TripDataProcessor(raw_data)
        elif platform_name.lower() == "ly":
            from flight_scraper.core.data.processor.ly_processor import LyDataProcessor
            return LyDataProcessor(raw_data)

        else:
            raise ValueError(f"不支持的平台: {platform_name}")