import os, json, requests
from datetime import datetime, timedelta

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
DISCORD_URL = os.getenv("DISCORD_WEBHOOK_URL")

def generate_report():
    with open('stock_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    tw_time = (datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M')
    
    # 鎖定台股與法人分析
    prompt = f"""
    你是總帥的台股戰略官。禁止廢話。
    數據: {json.dumps(data, ensure_ascii=False)}
    防線: 0050 25.4萬階梯防禦。
    
    任務:
    1. 分析 0050 價格與「25.4 萬」防線的距離。
    2. 深度解讀「三大法人買賣超」力道。
    3. 給出明日開盤前的防禦或進攻建議。
    4. 結尾：報告完畢，請總帥下令。
    """
    
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"
    response = requests.post(api_url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=30)
    report = response.json()["candidates"][0]["content"]["parts"][0]["text"]
    
    full_msg = f"🇹🇼 **【台股盤後法人戰報 - {tw_time}】**\n{report}"
    requests.post(DISCORD_URL, json={"content": full_msg})
    with open("report_tw.md", "w", encoding="utf-8") as f: f.write(full_msg)

if __name__ == "__main__": generate_report()
