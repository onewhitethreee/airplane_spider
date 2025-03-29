# 这是一个测试本地代理连接的小脚本。通过开启抓包软件Raqable，其端口为9000，另外我还开启了Warp，这样子能够隐藏个人的IP。防止IP为封掉
import requests
import urllib3

urllib3.disable_warnings()

proxies = {"http": "http://127.0.0.1:9000", "https": "http://127.0.0.1:9000"}

try:
    # 测试基本连接
    r = requests.get("https://httpbin.org/ip", proxies=proxies, verify=False)
    print(f"连接成功! 响应: {r.text}")
except Exception as e:
    r = requests.get("https://httpbin.org/ip")
    print("连接失败! 已切换到本地IP")
    print(f"响应: {r.text}")
