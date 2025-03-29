import sys
import os
import json
import logging
from typing import Dict, Any, List, Optional

# 设置日志配置
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 设置项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# 导入项目模块
from config.config_manager import ConfigManager
from config.json_parse import JsonParse
from airplane_platform.booking.booking_spider import Booking_spider
from notify.server_jiang import server_jiang


class FlightNotifier:
    """管理航班信息获取和通知的类"""

    def __init__(self):
        self.config_manager = ConfigManager()
        self.notify_config = self._load_notify_config()

    def _load_notify_config(self) -> Dict[str, Any]:
        """加载通知配置"""
        try:
            notify_config_path = os.path.join(
                project_root, "config/configs/nofity_config.json"
            )
            with open(notify_config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"通知配置文件未找到: {notify_config_path}")
            raise
        except json.JSONDecodeError:
            logger.error(f"通知配置文件格式错误: {notify_config_path}")
            raise

    def get_flight_info(self) -> str:
        """获取航班信息"""
        try:
            json_config = self.config_manager.register_parser(
                r"config/configs/config_booking.json", JsonParse
            )
            booking_spider = Booking_spider(json_config)
            return booking_spider.run()
        except Exception as e:
            logger.error(f"获取航班信息时出错: {str(e)}")
            raise

    def send_server_jiang_notification(self, title: str, content: str) -> bool:
        """发送Server酱通知"""
        try:
            if not self.notify_config.get("server_jiang", {}).get("enable", False):
                logger.info("Server酱通知未启用")
                return False

            logger.info("通过Server酱发送通知")
            response = server_jiang().main(title, content)

            if hasattr(response, "status_code") and 200 <= response.status_code < 300:
                logger.info(f"Server酱通知发送成功: {response.status_code}")
                return True
            else:
                logger.warning(
                    f"Server酱通知发送可能失败: {getattr(response, 'status_code', None)}"
                )
                return False
        except Exception as e:
            logger.error(f"发送Server酱通知时出错: {str(e)}")
            return False

    def send_telegram_notification(self, content: str) -> bool:
        """发送Telegram通知"""
        try:
            if not self.notify_config.get("telegram", {}).get("enable", False):
                logger.info("Telegram通知未启用")
                return False

            logger.info("Telegram通知功能尚未实现")
            # 这里可以添加Telegram通知的实现
            return False
        except Exception as e:
            logger.error(f"发送Telegram通知时出错: {str(e)}")
            return False

    def notify_all(self, title: str, content: Optional[str] = None) -> Dict[str, bool]:
        """发送所有已启用的通知"""
        if content is None:
            content = self.get_flight_info()

        results = {}

        # 发送Server酱通知
        results["server_jiang"] = self.send_server_jiang_notification(title, content)

        # 发送Telegram通知
        results["telegram"] = self.send_telegram_notification(content)

        return results


def main():
    """主函数"""
    try:
        notifier = FlightNotifier()
        title = "航班信息"
        results = notifier.notify_all(title)

        logger.info(f"通知发送结果: {results}")
    except Exception as e:
        logger.error(f"程序执行出错: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
