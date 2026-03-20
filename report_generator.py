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

    update_time = datetime.now().strftime('%Y-%m-%d %H:%M')
    defense_line = "VOOG 買跌不買漲、MU/NVDA 續抱、0050 25.4萬階梯防禦。"

    # --- 2. 執行 AI 戰略分析 (對齊 2026 最新型號) ---
    # 【最核心修正】使用您日誌中印出的精確路徑
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    prompt = f"你是總帥首席戰略官。請根據數據產出精簡戰報，使用 Markdown 表格與重點條列：{json.dumps(raw_data, ensure_ascii=False)}\n戰略防線：{defense_line}"
    
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
            print(f"API 拒絕請求，錯誤: {json.dumps(result)}")
            
    except Exception as e:
        print(f"分析崩潰: {str(e)}")

if __name__ == "__main__":
    generate_report()
