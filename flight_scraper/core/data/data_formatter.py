def format_time_duration(seconds) -> str:
    """将秒数格式化为小时和分钟"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours}h {minutes}m"

def parse_iso_time(time_str):
    """手动解析ISO格式时间字符串"""
    # 处理格式如：2025-07-14T10:15:00
    date_part, time_part = time_str.split('T')
    year, month, day = map(int, date_part.split('-'))
    hour, minute, second = map(int, time_part.split(':'))

    from datetime import datetime
    return datetime(year, month, day, hour, minute, second)


