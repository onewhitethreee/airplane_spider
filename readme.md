# 航班爬虫

一个综合性的航班票价信息爬虫，汇总多个平台的数据，帮助您找到最优惠的航班。

## 概述

本项目旨在从各个平台抓取航班信息，比较价格，并通知用户最优惠的航班。目前支持Booking.com，计划扩展到携程(Trip.com)和同程(Ly.com)。

## 功能特点

### 当前功能

- [x] **多平台支持**
  - [x] Booking.com
  - [ ] 携程(Trip.com)（计划中）
  - [ ] 同程(Ly.com)（计划中）

- [x] **高级搜索选项**
  - [x] 多日期搜索（在一段时间内找到最便宜的航班）
  - [x] 往返搜索
  - [x] 可自定义舱位等级、乘客数量

- [x] **数据处理**
  - [x] 按价格排序
  - [x] 按航空公司筛选
  - [x] 按中转次数筛选
  - [x] 按行李额筛选

- [x] **通知系统**
  - [x] Server酱集成
  - [ ] Telegram通知（计划中）

- [x] **导出格式**
  - [x] Excel导出
  - [x] CSV导出
  - [x] 纯文本输出

### 筛选功能

以下筛选和排序选项可通过Excel使用：

- [x] 按价格排序
- [x] 按出发/到达时间排序
- [x] 按航空公司排序
- [x] 按中转次数排序
- [x] 按行李额排序

## 安装

### 要求

- Python 3.7+
- 所需包（通过`pip install -r requirements.txt`安装）:
  - requests
  - pandas
  - openpyxl
  - python-dotenv

### 设置

1. 克隆仓库:
```bash
git clone https://github.com/yourusername/flight-scraper.git
cd flight-scraper
```

2. 安装依赖:
```bash
pip install -r requirements.txt
```

3. 配置搜索参数:
   - 编辑`config/configs/config_booking.json`设置您的搜索条件
   - 示例:
   ```json
   {
     "booking": {
       "api_url": "https://flights.booking.com/api/flights/",
       "booking_search_condition": {
         "type": "ROUNDTRIP",
         "adults": "1",
         "cabinClass": "ECONOMY",
         "children": "",
         "from": "MAD.AIRPORT",
         "to": "SHA.CITY",
         "depart": "2025-07-14",
         "return": "2025-08-19",
         "sort": "CHEAPEST"
       },
       "proxies": {
         "proxy1": {
           "host": "proxy1.com",
           "port": "8080",
           "username": "user1",
           "password": "pass1"
         }
       }
     }
   }
   ```

4. 配置通知服务（可选）:
   - 编辑`config/configs/nofity_config.json`启用或禁用通知服务
   - 对于Server酱，在项目根目录创建一个`.env`文件:
   ```
   SERVER_API_KEY=your_server_jiang_key
   ```

## 使用方法

### 基本用法

运行主脚本搜索航班:

```bash
python src/main.py
```

### 高级选项

```bash
python src/main.py --start-date 2025-07-15 --days-range 10 --return-days 36 --top-n 5 --save-excel
```

命令行参数:

- `--start-date`: 搜索起始日期（格式：YYYY-MM-DD）
- `--days-range`: 从起始日期开始搜索的天数（默认：1）
- `--return-days`: 停留时间长度（默认：36）
- `--top-n`: 显示最便宜的航班数量（默认：5）
- `--title`: 自定义通知标题
- `--no-notify`: 不发送通知，仅保存到文件
- `--save-csv`: 将结果保存为CSV
- `--save-excel`: 将结果保存为Excel（默认启用）

## 项目结构

该项目遵循模块化设计，主要组件如下:

- `config/`: 配置管理
- `flight_scraper/`: 核心爬虫功能
  - `core/`: 抽象类和通用工具
  - `platforms/`: 平台特定实现
- `notify/`: 通知服务
- `src/`: 主应用程序代码

完整概览请参阅[目录结构](structure.md)。

## 开发状态

本项目正在积极开发中:

- [x] 完成Booking.com爬虫
- [x] 实现Booking.com多日期搜索
- [x] 添加Server酱通知
- [ ] 实现携程(Trip.com)爬虫
- [ ] 实现同程(Ly.com)爬虫
- [ ] 添加Telegram通知

## 未来计划

- 多语言支持（中文和英文）
- 邮件通知
- 移动应用集成
- 更多筛选选项
- 航班价格历史追踪
- 价格提醒功能

## 免责声明

这是一个非商业项目，仅为个人使用而创建，用于汇总航班信息和便于旅行计划。请按照航班预订平台的服务条款负责任地使用。

## 许可

本项目是开源的，使用MIT许可证。