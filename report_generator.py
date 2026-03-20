import os
import json
import requests
from datetime import datetime, timedelta

# --- 1. 安全初始化 ---
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
DISCORD_URL = os.getenv("DISCORD_WEBHOOK_URL")

def send_discord_notify(message):
    # 強力分段：每 1000 字切一段，確保 Discord 絕對不會漏字
    for i in range(0, len(message), 1000):
        part = message[i:i+1000]
        requests.post(DISCORD_URL, json={"content": part}, timeout=10)

def generate_report():
    file_path = 'stock_data.json'
    if not os.path.exists(file_path): return

    with open(file_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    tw_time = (datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M')
    
    # --- 2. 深度分析指令：解除封印 ---
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"
    
    prompt = f"""
    你是總帥的首席戰略顧問。現在有一份敵後情報，請給出硬核、無廢話、充滿洞見的戰略報告。
    
    【敵後情報 (數據)】: {json.dumps(raw_data, ensure_ascii=False)}
    【當前防線】: VOOG下殺點射、MU/NVDA續抱、0050 25.4萬階梯防禦。
    
    【⚠️ 戰略分析鐵律】:
    1. 📊 **數據深度解碼**: 必須逐一提到數據中的標的(如0050或其他)，並比對當前價格與防線距離。
    2. 📡 **戰情局勢**: 用軍事術語分析今日多空交戰態勢。
    3. ⚔️ **具體戰術行動**: 告訴總帥現在是要「按兵不動」、「埋伏點射」還是「全面撤退」。
    4. 必須使用 Markdown 粗體強調關鍵字。內容要飽滿，不要精簡，把事情講透。
    5. 結尾：回報「報告完畢，請總帥下令。」
    """
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 2000, # 給 AI 空間發揮
            "temperature": 0.8
        }
    }
    
    try:
        response = requests.post(api_url, json=payload, timeout=30)
        result = response.json()
        
        if "candidates" in result:
            report_text = result["candidates"][0]["content"]["parts"][0]["text"]
            header = f"📡 **【總帥盤後硬核深度戰報 - {tw_time} (TW)】**\n"
            send_discord_notify(header + report_text)
        else:
            print(f"AI 異常: {result}")
            
    except Exception as e:
        print(f"分析崩潰: {str(e)}")

if __name__ == "__main__":
    generate_report()
