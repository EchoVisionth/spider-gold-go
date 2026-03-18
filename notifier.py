import os
import json
import datetime
import firebase_admin
from firebase_admin import credentials, messaging

def send_push_notification(test_mode=False):
    """
    发送金价更新通知 (支持中、泰、英三语)
    """
    # 严格从环境变量读取 (GitHub Actions 安全规范)
    service_account_info = os.environ.get('FIREBASE_SERVICE_ACCOUNT')

    if not service_account_info:
        print("Error: FIREBASE_SERVICE_ACCOUNT environment variable not set.")
        return

    try:
        # 初始化 Firebase
        cert_dict = json.loads(service_account_info)
        cred = credentials.Certificate(cert_dict)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)

        # 检查逻辑：今天是否有价格更新 (YYYY-MM-DD)
        today_str = datetime.datetime.now().strftime('%Y-%m-%d')
        
        if not test_mode:
            if not os.path.exists('price_history.json'):
                print("Error: price_history.json not found.")
                return
            
            with open('price_history.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                history = data.get('history', [])
                
                # 获取最新的一条数据
                latest_entry = history[0] if history else None
                if not latest_entry or latest_entry.get('date') != today_str:
                    print(f"Skipping: No update found for today ({today_str}).")
                    return
                print(f"Found update for {today_str}. Proceeding to send notifications...")

        # 定义多语言推送任务
        tasks = [
            {
                "topic": "gold_updates_zh",
                "title": "【Gold Go】每日行情快报 📈",
                "body": f"今日（{today_str}）金价已实时更新。数据源已同步，请点击查看您的持仓实时盈亏及最新趋势。"
            },
            {
                "topic": "gold_updates_th",
                "title": "【Gold Go】รายงานราคาทองวันนี้ 📈",
                "body": f"ราคาทองประจำวันที่ {today_str} อัปเดตแล้ว ข้อมูลจากสมาคมฯ พร้อมใช้งาน โปรดตรวจสอบกำไร/ขาดทุนพอร์ตของคุณตอนนี้"
            },
            {
                "topic": "gold_updates_en",
                "title": "【Gold Go】Daily Gold Report 📈",
                "body": f"Today's ({today_str}) gold prices are updated. Data synced. Click to view your real-time portfolio performance and trends."
            }
        ]

        # 循环发送
        for task in tasks:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=task["title"],
                    body=task["body"],
                ),
                topic=task["topic"],
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        channel_id='gold_updates_channel',
                        icon='launcher_icon',
                        color='#FFD700',
                        sound='default'
                    )
                )
            )
            response = messaging.send(message)
            print(f'Successfully sent to {task["topic"]}: {response}')

    except Exception as e:
        print(f"Failed to send push notification: {e}")

if __name__ == "__main__":
    import sys
    is_test = "--test" in sys.argv
    send_push_notification(test_mode=is_test)
