import os
import json
import requests
from datetime import datetime, timedelta

# --- 1. 安全初始化 ---
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
DISCORD_URL = os.getenv("DISCORD_WEBHOOK_URL")

def send_discord_notify(message):
    for i in range(0, len(message), 1000):
        part = message[i:i+1000]
        requests.post(DISCORD_URL, json={"content": part}, timeout=10)

def generate_report():
    file_path = 'stock_data.json'
    if not os.path.exists(file_path): return

    with open(file_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    tw_time = (datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M')
    
    # --- 2. 斷絕式指令：嚴禁廢話 ---
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"
    
    prompt = f"""
    你是總帥的戰略副官。禁止任何問候語，直接進入數據分析。
    
    【情報數據】: {json.dumps(raw_data, ensure_ascii=False)}
    【戰略防線】: VOOG下殺點射、MU/NVDA續抱、0050 25.4萬階梯防禦。
    
    【⚠️ 強制戰報規範】:
    1. **直接列出數據清單**：將 JSON 內的每個代碼(code)與名稱(name)，用 Markdown 表格或條列列出價格(close)。
    2. **對比防線**：計算數據中的標的與「25.4 萬」或「買綠不買紅」防線的距離，給出評價。
    3. **最終指令**：用粗體寫下今日具體該做的事（如：點射 1 股、繼續埋伏、不可追高）。
    4. 禁止說「以下為報告」、「研判刻不容緩」等廢話。違者重罰。
    """
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 1500,
            "temperature": 0.4 # 降低溫度，讓它說話更死板、更注重數字
        }
    }
    
    try:
        response = requests.post(api_url, json=payload, timeout=30)
        result = response.json()
        
        if "candidates" in result:
            report_text = result["candidates"][0]["content"]["parts"][0]["text"]
            # 物理性砍掉 AI 可能吐出的開場白 (如果它不聽話)
            clean_text = report_text.replace("總帥，", "").replace("以下是您的戰報", "").strip()
            
            header = f"📡 **【總帥盤後數據戰報 - {tw_time}】**\n"
            send_discord_notify(header + clean_text)
        else:
            print(f"AI 異常: {result}")
            
    except Exception as e:
        print(f"分析崩潰: {str(e)}")

if __name__ == "__main__":
    generate_report()
