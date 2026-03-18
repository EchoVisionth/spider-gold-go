"""
Gold Go - 收盘价更新脚本
每天 17:30 运行，从自建 API 获取当日收盘价并更新到 price_history.json
新格式：最新日期在最前面，包含买卖双向价格
"""

import requests
import json
import os
from datetime import datetime

# 自建 API
API_URL = "https://gold-price-api.goldgo.workers.dev"
HISTORY_FILE = "price_history.json"


def load_history():
    """加载历史价格数据"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"history": [], "total_days": 0}


def save_history(data):
    """保存历史价格数据"""
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def fetch_latest_price():
    """从自建 API 获取最新价格"""
    try:
        print(f"Fetching from: {API_URL}")
        response = requests.get(API_URL, timeout=30)
        
        if response.status_code != 200:
            print(f"API returned status: {response.status_code}")
            return None
        
        data = response.json()
        
        if data.get('status') != 'success':
            print(f"API status not success: {data.get('status')}")
            return None
        
        return data.get('data')
        
    except Exception as e:
        print(f"Error fetching price: {e}")
        return None


def update_closing_price():
    """更新收盘价到历史记录"""
    print("=" * 60)
    print("Gold Go - 收盘价更新")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 获取最新价格
    price_data = fetch_latest_price()
    
    if not price_data:
        print("Failed to fetch latest price")
        return False
    
    today_date = price_data.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    print(f"\n获取到价格数据:")
    print(f"  日期: {today_date}")
    print(f"  时间: {price_data.get('update_time')}")
    print(f"  金条: 买入={price_data.get('bar_gold', {}).get('buy_price')}, 卖出={price_data.get('bar_gold', {}).get('sell_price')}")
    print(f"  金饰: 买入={price_data.get('ornament_gold', {}).get('buy_price')}, 卖出={price_data.get('ornament_gold', {}).get('sell_price')}")
    
    # 加载历史数据
    history_data = load_history()
    history = history_data.get('history', [])
    
    # 构建今日记录（新格式，已移除 change_count）
    new_record = {
        "date": today_date,
        "update_time": price_data.get('update_time', '17:30'),
        "bar_buy": price_data.get('bar_gold', {}).get('buy_price', 0),
        "bar_sell": price_data.get('bar_gold', {}).get('sell_price', 0),
        "ornament_buy": price_data.get('ornament_gold', {}).get('buy_price', 0),
        "ornament_sell": price_data.get('ornament_gold', {}).get('sell_price', 0)
    }
    
    # 检查是否已有今日记录（在列表最前面查找）
    existing_index = None
    for i, record in enumerate(history):
        if record.get('date') == today_date:
            existing_index = i
            break
    
    if existing_index is not None:
        # 更新现有记录
        history[existing_index] = new_record
        print(f"\n更新现有记录: {today_date}")
    else:
        # 添加新记录到最前面（保持最新日期在前）
        history.insert(0, new_record)
        print(f"\n添加新记录: {today_date}")
    
    # 更新元数据
    history_data['history'] = history
    history_data['total_days'] = len(history)
    history_data['last_updated'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S+07:00')
    
    # 保存
    save_history(history_data)
    
    print(f"历史记录总数: {len(history)}")
    print("\n✅ 收盘价更新完成!")
    
    return True


if __name__ == "__main__":
    success = update_closing_price()
    exit(0 if success else 1)
