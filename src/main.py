import sys
import os
import json
import logging
from typing import Dict, Any, List, Optional

from notify.server_jiang import server_jiang

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
from flight_scraper.core.factory.factory import ScraperFactory


class FlightNotifier:
    """管理航班信息获取和通知的类"""

    def __init__(self):
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

    def get_flight_info(self, platform: str = "booking") -> str:
        """获取航班信息

        Args:
            platform: 平台名称，默认为booking

        Returns:
            str: 航班信息
        """
        try:
            # 使用工厂模式创建爬虫实例
            scraper = ScraperFactory.create_scraper(platform)
            return scraper.run()
        except Exception as e:
            logger.error(f"获取{platform}平台航班信息时出错: {str(e)}")
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

    def notify_all(self, title: str, content: Optional[str] = None, platform: str = "booking") -> Dict[str, bool]:
        """发送所有已启用的通知

        Args:
            title: 通知标题
            content: 通知内容，如果为None则获取航班信息
            platform: 爬取平台，默认为booking

        Returns:
            Dict[str, bool]: 各通知渠道的发送结果
        """
        if content is None:
            content = self.get_flight_info(platform)

        results = {}

        # 发送Server酱通知
        results["server_jiang"] = self.send_server_jiang_notification(title, content)

        # 发送Telegram通知
        results["telegram"] = self.send_telegram_notification(content)

        # 如果所有通知渠道都未启用或发送失败，保存到文件
        if not any(results.values()):
            self._save_to_file(title, content)
            results["file"] = True

        return results

    def _save_to_file(self, title: str, content: str) -> None:
        """将内容保存到文件"""
        try:
            # 创建输出目录（如果不存在）
            output_dir = os.path.join(project_root, "output")
            os.makedirs(output_dir, exist_ok=True)

            # 生成文件名（使用标题和日期）
            from datetime import datetime

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{title.replace(' ', '_')}_{timestamp}.txt"
            filepath = os.path.join(output_dir, filename)

            # 保存内容到文件
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

            logger.info(f"内容已保存到文件: {filepath}")
        except Exception as e:
            logger.error(f"保存内容到文件时出错: {str(e)}")


def main():
    """主函数"""
    try:
        # 解析命令行参数
        import argparse
        parser = argparse.ArgumentParser(description="航班信息爬取和通知工具")
        parser.add_argument("--platform", type=str, default="booking",
                            help="爬取平台，例如booking、expedia等")
        parser.add_argument("--title", type=str, default="航班信息",
                            help="通知标题")
        args = parser.parse_args()

        notifier = FlightNotifier()
        results = notifier.notify_all(args.title, platform=args.platform)

        logger.info(f"通知发送结果: {results}")

        # 检查是否有配置启用
        if not any(
                [
                    notifier.notify_config.get("server_jiang", {}).get("enable", False),
                    notifier.notify_config.get("telegram", {}).get("enable", False),
                ]
        ):
            logger.info("所有通知渠道均未启用，结果已保存到文件")

    except Exception as e:
        logger.error(f"程序执行出错: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())