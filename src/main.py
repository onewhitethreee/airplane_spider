# src/multi_date_search.py
import sys
import os
import json
import logging
import argparse
from datetime import datetime

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
from flight_scraper.platforms.booking.multi_date_scraper import MultiDateBookingScraper
from config.json_parse import JsonParse
from config.config_manager import ConfigManager
from notify.server_jiang import server_jiang


def load_booking_config():
    """加载Booking配置"""
    config_manager = ConfigManager()
    return config_manager.register_parser(
        os.path.join(project_root, "config", "configs", "config_booking.json"),
        JsonParse
    )


def load_notify_config():
    """加载通知配置"""
    config_manager = ConfigManager()
    return config_manager.register_parser(
        os.path.join(project_root, "config", "configs", "nofity_config.json"),
        JsonParse
    )


def send_notification(title, content, notify_config):
    """发送通知"""
    # 检查Server酱是否启用
    if notify_config.get("server_jiang", {}).get("enable", True):
        logger.info("通过Server酱发送通知")
        server_jiang().main(title, content)
    else:
        logger.info("Server酱通知未启用")

    # 保存到文件
    output_dir = os.path.join(project_root, "output")
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{title.replace(' ', '_')}_{timestamp}.txt"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    logger.info(f"内容已保存到文件: {filepath}")


def main():
    """主函数"""
    try:
        # 解析命令行参数
        parser = argparse.ArgumentParser(description="多日期航班搜索工具")
        parser.add_argument("--start-date", type=str, default=None,
                            help="开始日期，格式为YYYY-MM-DD")
        parser.add_argument("--days-range", type=int, default=10,
                            help="出发日期范围天数，默认为10天")
        parser.add_argument("--return-days", type=int, default=36,
                            help="返程天数，默认为36天")
        parser.add_argument("--top-n", type=int, default=5,
                            help="显示前几个最便宜的航班，默认为5个")
        parser.add_argument("--title", type=str, default="十天内最便宜航班信息",
                            help="通知标题")
        parser.add_argument("--no-notify", action="store_true",
                            help="不发送通知，只保存到文件")
        args = parser.parse_args()

        # 如果未指定开始日期，使用配置中的日期
        booking_config = load_booking_config()
        if args.start_date is None:
            args.start_date = booking_config["booking"]["booking_search_condition"]["depart"]
            logger.info(f"使用配置中的出发日期: {args.start_date}")

        # 创建多日期爬虫
        multi_date_scraper = MultiDateBookingScraper(booking_config)

        # 运行爬虫
        logger.info(f"开始爬取从 {args.start_date} 起的 {args.days_range} 天内最便宜航班...")
        results = multi_date_scraper.run(
            args.start_date,
            args.days_range,
            args.return_days,
            args.top_n
        )

        # 发送通知
        if not args.no_notify:
            notify_config = load_notify_config()
            send_notification(args.title, results, notify_config)
        else:
            # 直接打印结果
            print(results)

        logger.info("多日期航班搜索完成")

    except Exception as e:
        logger.error(f"程序执行出错: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())