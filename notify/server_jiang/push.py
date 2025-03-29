import os
import requests
import logging

class server_jiang:
    def __init__(self, key=None):
        # 尝试从多个来源获取密钥
        self.key = key

        # 如果没有直接提供密钥，尝试从环境变量获取
        if not self.key:
            self.key = os.environ.get("SERVER_CHAN_KEY")

        # 尝试从文件读取
        if not self.key and os.path.exists("server_api_key.txt"):
            try:
                with open("server_api_key.txt", "r") as f:
                    self.key = f.read().strip()
            except:
                pass

        if not self.key:
            raise ValueError(
                "请提供Server酱的API密钥或设置SERVER_CHAN_KEY环境变量或在server_api_key.txt文件中设置密钥"
            )

        self.url = f"https://sc.ftqq.com/{self.key}.send"
        self.headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        }

    def send(self, title, content):
        data = {"text": title, "desp": content}
        response = requests.post(self.url, headers=self.headers, data=data)
        return response

    def main(self, title, content):
        return self.send(title, content)


if __name__ == "__main__":
    # # 从文件读取航班信息内容
    # with open("flights_info.txt", "r", encoding="utf-8") as f:
    #     flight_info = f.read()

    # # 发送通知
    # title = "航班信息"
    # response = server_jiang().main(title, flight_info)

    # # 打印发送结果
    # logging.info(f"发送状态码: {response.status_code}")
    # logging.info(f"发送响应: {response.text}")
    logging.info("server酱模块已经初始化")