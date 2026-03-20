import os, json, requests
from datetime import datetime, timedelta

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
DISCORD_URL = os.getenv("DISCORD_WEBHOOK_URL")

def generate_report():
    with open('stock_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    tw_time = (datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M')
    
    # 鎖定美股標的分析
    prompt = f"""
    你是總帥的美股戰略官。禁止廢話。
    數據: {json.dumps(data, ensure_ascii=False)}
    防線: VOOG見綠點射、MU/NVDA續抱。
    
    任務:
    1. 僅提取美股標的價格。
    2. 判斷昨日收盤是否符合「下殺點射」時機。
    3. 給出今日開盤前的具體行動指令。
    4. 結尾：報告完畢，請總帥下令。
    """
    
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"
    response = requests.post(api_url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=30)
    report = response.json()["candidates"][0]["content"]["parts"][0]["text"]
    
    full_msg = f"🇺🇸 **【美股晨間戰報 - {tw_time}】**\n{report}"
    requests.post(DISCORD_URL, json={"content": full_msg})
    with open("report_us.md", "w", encoding="utf-8") as f: f.write(full_msg)

if __name__ == "__main__": generate_report()
