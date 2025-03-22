# 这是用来初始化booking模块的文件，主要是用来初始化booking模块的配置信息，

class Booking:

    def __init__(self, booking_search_condition):
        self._booking_search_condition = booking_search_condition["booking"][
            "booking_search_condition"
        ]
        self._booking_api_url = booking_search_condition["booking"]["api_url"]
    """
    booking search condition getter method
    """
    @property
    def booking_search_condition(self):
        return self._booking_search_condition

    """
    booking api url getter method
    """
    @property
    def booking_api_url(self):
        return self._booking_api_url
    


