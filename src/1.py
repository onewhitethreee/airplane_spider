import os
import requests
import json


url = "https://hk.trip.com/restapi/soa2/27015/FlightListSearch"

payload = {
  "mode": 1,
  "searchCriteria": {
    "grade": 3,
    "tripType": 2,
    "journeyNo": 1,
    "passengerInfoType": {
      "adultCount": 1,
      "childCount": 0,
      "infantCount": 0
    },
    "journeyInfoTypes": [
      {
        "journeyNo": 1,
        "departDate": "2025-07-08",
        "departCode": "MAD",
        "arriveCode": "WNZ",
        "departAirport": "",
        "arriveAirport": ""
      },
      {
        "journeyNo": 2,
        "departDate": "2025-08-20",
        "departCode": "WNZ",
        "arriveCode": "MAD",
        "departAirport": "",
        "arriveAirport": ""
      }
    ],

  },
  "sortInfoType": {
    "direction": True,
    "orderBy": "Direct",
    "topList": []
  },
  "tagList": [],
  "flagList": [],
  "filterType": {
    "filterFlagTypes": [],
    "queryItemSettings": [],
    "studentsSelectedStatus": True
  },

  "head": {
    "cid": "09034092115025308870",


    "extension": [

      {
        "name": "source",
        "value": "ONLINE"
      },
      {
        "name": "sotpGroup",
        "value": "Trip"
      },
      {
        "name": "sotpLocale",
        "value": "zh-CN"
      },
      {
        "name": "sotpCurrency",
        "value": "EUR"
      },


      {
        "name": "flt_app_session_transactionId",
        "value": "1-mf-20250407014048403-WEB"
      },
    ],
  }
}

headers = {
  'x-ctx-ubt-vid': "123" # 随机值都可以, 但是不能为空
}

# response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)
# response.raise_for_status()
# print(response.text)
# with open("response.json", "w") as f:
#     f.write(response.text)
from config.json_parse import JsonParse
from config.config_manager import ConfigManager
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)
def load_trip_config():
    config_manager = ConfigManager()
    return config_manager.register_parser(
        os.path.join(project_root, "config", "configs", "config_trip.json"),
        JsonParse
    )

config = load_trip_config()
print(config)
