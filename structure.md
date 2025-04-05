flight-scraper/
├── config/
│   ├── __init__.py              # 基础配置类
│   ├── config_manager.py        # 配置管理器
│   ├── json_parse.py            # JSON配置解析器
│   └── configs/
│       ├── config_booking.json  # Booking平台配置
│       └── nofity_config.json   # 通知设置
│
├── flight_scraper/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── abstract/
│   │   │   ├── __init__.py
│   │   │   └── abstract_methods.py  # 爬虫的抽象基类
│   │   ├── data/
│   │   │   ├── __init__.py
│   │   │   ├── data_formatter.py    # 数据格式化工具
│   │   │   ├── data_models.py       # 航班信息的数据模型
│   │   │   └── processor/
│   │   │       ├── __init__.py
│   │   │       ├── booking_processor.py  # Booking数据处理器
│   │   │       ├── data_processor.py     # 基础数据处理器
│   │   │       └── processor_factory.py  # 数据处理器工厂
│   │   ├── factory/
│   │   │   ├── __init__.py
│   │   │   └── factory.py       # 爬虫创建工厂
│   │   └── platform_config.py   # 平台配置基类
│   ├── platforms/
│   │   ├── __init__.py
│   │   ├── booking/
│   │   │   ├── __init__.py
│   │   │   ├── config.py        # Booking配置
│   │   │   ├── multi_date_scraper.py  # Booking多日期爬虫
│   │   │   └── scraper.py       # Booking爬虫实现
│   │   ├── ly/
│   │   │   └── __init__.py      # 同程（Ly.com）实现占位符
│   │   └── trip/
│   │       └── __init__.py      # 携程（Trip.com）实现占位符
│   ├── proxy/
│   │   └── __init__.py          # IP代理处理
│   ├── test/
│   │   └── configTest.py        # 配置单元测试
│   └── verifycode/
│       └── __init__.py          # 验证码处理
│
├── notify/
│   ├── __init__.py
│   ├── readme.md                # 通知模块文档
│   ├── server_jiang/
│   │   ├── __init__.py
│   │   └── push.py              # Server酱通知实现
│   └── telegram/
│       ├── __init__.py
│       └── push.py              # Telegram通知实现
│
├── output/                      # 结果保存目录
│
├── script/
│   └── ip_cheker.py             # IP和代理状态检查工具
│
├── src/
│   └── main.py                  # 主应用程序入口点
│
├── readme.md                    # 项目说明
└── 目录结构.md                   # 原始目录结构文档