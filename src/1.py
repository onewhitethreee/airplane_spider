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
        "departDate": "2025-07-14",
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
        "value": "zh-HK"
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
  'x-ctx-ubt-vid': "123" # 随机值都可以

}

response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)
response.raise_for_status()
print(response.text)