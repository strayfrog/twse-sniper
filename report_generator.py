import os
import json
import requests
from datetime import datetime, timedelta

# --- 1. 安全初始化 ---
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
DISCORD_URL = os.getenv("DISCORD_WEBHOOK_URL")

def send_discord_notify(message):
    # Discord 限制 2000 字元，我們將長文拆分發送
    if len(message) <= 2000:
        requests.post(DISCORD_URL, json={"content": message}, timeout=10)
    else:
        # 超長時分段發送
        for i in range(0, len(message), 1900):
            part = message[i:i+1900]
            requests.post(DISCORD_URL, json={"content": f"(續前報...)\n{part}"}, timeout=10)

def generate_report():
    file_path = 'stock_data.json'
    if not os.path.exists(file_path): return

    with open(file_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    # 【時區修正】強制轉換為台灣時間 (UTC+8)
    tw_time = (datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M')
    
    # --- 2. 執行 AI 戰略分析 ---
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"
    
    prompt = f"""
    你是總帥的首席戰略官。請針對以下情報進行硬核分析：
    【當前情報】: {json.dumps(raw_data, ensure_ascii=False)}
    【防線】: VOOG下殺點射、MU/NVDA續抱、0050 25.4萬階梯防禦。
    
    【⚠️ 強制要求】:
    1. 分為：[📡戰情總結]、[📊數據透視]、[⚔️行動建議]。
    2. 使用條列式，禁止長篇大論。
    3. 每段重點用粗體。
    4. 結尾必須回報「報告完畢，請總帥下令。」
    """
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": 1000, "temperature": 0.5}
    }
    
    try:
        response = requests.post(api_url, json=payload, timeout=30)
        result = response.json()
        
        if "candidates" in result:
            report_text = result["candidates"][0]["content"]["parts"][0]["text"]
            full_message = f"📡 **【總帥盤後硬核戰報 - {tw_time} (TW)】**\n{report_text}"
            send_discord_notify(full_message)
        else:
            print(f"AI 異常: {result}")
            
    except Exception as e:
        print(f"分析崩潰: {str(e)}")

if __name__ == "__main__":
    generate_report()
