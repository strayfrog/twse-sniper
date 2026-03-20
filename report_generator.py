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
        print(f"Discord 回傳狀態: {r.status_code}")
    except Exception as e:
        print(f"發送失敗: {e}")

def generate_report():
    file_path = 'stock_data.json'
    if not os.path.exists(file_path):
        print("找不到 stock_data.json")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    update_time = datetime.now().strftime('%Y-%m-%d %H:%M')
    defense_line = "VOOG 買跌不買漲、MU/NVDA 續抱、0050 25.4萬階梯防禦。"

    # --- 2. 執行 AI 戰略分析 (降級相容版本) ---
    # 【關鍵修正】模型名稱改為最通用的 gemini-pro
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    prompt = f"你是總帥首席戰略官。根據數據產出精簡戰報：{json.dumps(raw_data, ensure_ascii=False)}\n戰略防線：{defense_line}"
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        result = response.json()
        
        if "candidates" in result:
            report_text = result["candidates"][0]["content"]["parts"][0]["text"]
            full_message = f"📡 **【總帥盤後戰報 - {update_time}】**\n{report_text}"
            send_discord_notify(full_message)
        else:
            # 如果還是失敗，我們會看到 Google 給的具體錯誤原因
            print(f"API 拒絕請求。錯誤訊息: {json.dumps(result)}")
            
    except Exception as e:
        print(f"通訊失敗: {str(e)}")

if __name__ == "__main__":
    generate_report()
