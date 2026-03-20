import os
import json
import requests
from datetime import datetime

# --- 1. 安全初始化 ---
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
DISCORD_URL = os.getenv("DISCORD_WEBHOOK_URL")

def send_discord_notify(message):
    # Discord Webhook 單次發送上限為 2000 字元，我們截斷確保安全
    safe_message = message[:1950] 
    payload = {"content": safe_message}
    try:
        r = requests.post(DISCORD_URL, json=payload, timeout=10)
        print(f"Discord 發送狀態: {r.status_code}")
        if r.status_code != 204:
            print(f"Discord 回傳錯誤詳情: {r.text}")
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
    defense_line = "VOOG 下殺點射、MU/NVDA 續抱、0050 25.4萬防禦。"

    # --- 2. 執行 AI 戰略分析 (2026 最新模型) ---
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    # 限制 AI 輸出的長度與格式
    prompt = f"你是總帥首席戰略官。請根據數據產出精簡戰報，限 500 字內，使用簡單條列式即可：{json.dumps(raw_data, ensure_ascii=False)}\n戰略防線：{defense_line}"
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 800,
            "temperature": 0.7
        }
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        result = response.json()
        
        if "candidates" in result:
            report_text = result["candidates"][0]["content"]["parts"][0]["text"]
            # 加上明顯的標題
            full_message = f"📡 **【總帥盤後戰報 - {update_time}】**\n{report_text}"
            send_discord_notify(full_message)
        else:
            print(f"AI 異常: {json.dumps(result)}")
            
    except Exception as e:
        print(f"分析崩潰: {str(e)}")

if __name__ == "__main__":
    generate_report()
