import os
import json
import requests
from datetime import datetime

# --- 1. 安全初始化 ---
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
DISCORD_URL = os.getenv("DISCORD_WEBHOOK_URL")

def send_discord_notify(message):
    payload = {"content": message}
    try:
        r = requests.post(DISCORD_URL, json=payload, timeout=10)
        print(f"Discord 發送狀態: {r.status_code}")
    except Exception as e:
        print(f"發送失敗: {e}")

def generate_report():
    file_path = 'stock_data.json'
    if not os.path.exists(file_path):
        print("找不到 stock_data.json")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    # --- 2. 核心診斷：要求模型列表 ---
    list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_KEY}"
    try:
        models_resp = requests.get(list_url)
        print("--- 可用模型列表診斷 ---")
        print(models_resp.text[:500]) # 印出前 500 字看可用型號
    except:
        print("無法取得模型列表")

    # --- 3. 強制發送測試 (跳過 AI) ---
    update_time = datetime.now().strftime('%Y-%m-%d %H:%M')
    test_msg = f"📡 **【系統診斷訊息 - {update_time}】**\n目前 AI 連線受阻，正在強制發送數據：\n{json.dumps(raw_data, ensure_ascii=False)}"
    
    send_discord_notify(test_msg)

if __name__ == "__main__":
    generate_report()
