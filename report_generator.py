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

    # 【🛡️ 總帥 2026 全球資產戰略防線】
    defense_line = "美股 VOOG 下殺點射、MU/MUU/NVDA 續抱、台股 0050 25.4萬防禦。"

    # --- 2. 執行 AI 戰略分析 (直接使用 HTTP POST) ---
    # 【核心修正】強制鎖定 v1 穩定版 URL
    api_url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    prompt = f"你是總帥首席戰略官。請根據數據產出精簡戰報：{json.dumps(raw_data, ensure_ascii=False)}\n戰略防線：{defense_line}"
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        result = response.json()
        
        # 解析返回內容
        if "candidates" in result:
            report_text = result["candidates"][0]["content"]["parts"][0]["text"]
            full_message = f"📡 **【總帥盤後戰報 - {update_time}】**\n{report_text}"
            send_discord_notify(full_message)
        else:
            print(f"API 錯誤回應: {json.dumps(result)}")
            
    except Exception as e:
        print(f"AI 請求失敗: {str(e)}")

if __name__ == "__main__":
    generate_report()
