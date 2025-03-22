import requests

url = "https://flights.booking.com/api/flights/"
proxies = {
    "http": "http://127.0.0.1:9000",  # 根据你的抓包软件调整端口
    "https": "http://127.0.0.1:9000",  # 许多抓包工具默认使用8888端口
}
params = {
    "type": "ROUNDTRIP",
    "adults": "1",
    "cabinClass": "ECONOMY",
    "children": "",
    "from": "MAD.AIRPORT",
    "to": "SHA.CITY",
    "depart": "2025-07-14",
    "return": "2025-08-14",
    "sort": "CHEAPEST",
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
}

response = requests.get(url, params=params, headers=headers, proxies=proxies, verify=False)

with open("flightss.json", "w", encoding='utf-8') as f:
    f.write(response.text)
