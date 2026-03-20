import os
import json
import requests
from datetime import datetime, timedelta

# --- 1. 初始化 ---
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
    
    # --- 2. 深度分析指令 ---
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"
    
    prompt = f"""
    你是總帥的戰略副官。禁止廢話，直接進入硬核分析。
    
    【情報數據】: {json.dumps(raw_data, ensure_ascii=False)}
    【戰略防線】: VOOG買綠不買紅、MU/NVDA續抱、0050 25.4萬階梯防禦。
    
    【戰報規範】:
    1. 📊 **數據清單**: 條列 JSON 內標的之價格。
    2. ⚔️ **具體戰略建議**: 比對 25.4 萬防線給出行動計畫。
    3. 語氣冷酷、嚴禁任何開場白。
    """
    
    try:
        response = requests.post(api_url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=30)
        result = response.json()
        
        if "candidates" in result:
            report_text = result["candidates"][0]["content"]["parts"][0]["text"]
            full_content = f"# 📡 總帥盤後硬核戰報 - {tw_time}\n\n{report_text}"
            
            # 【關鍵：本地存檔】
            with open("latest_report.md", "w", encoding="utf-8") as f:
                f.write(full_content)
            
            # 同步發 Discord
            send_discord_notify(full_content)
        else:
            print(f"AI 異常: {result}")
            
    except Exception as e:
        print(f"分析失敗: {str(e)}")

if __name__ == "__main__":
    generate_report()
