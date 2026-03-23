import os, json, requests
from datetime import datetime, timedelta

# --- 初始化 ---
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
DISCORD_URL = os.getenv("DISCORD_WEBHOOK_URL")

def generate_report():
    if not os.path.exists('stock_data.json'): return
    with open('stock_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    tw_time = (datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M')
    
    # 【核心升級：深度美股戰略指令】
    prompt = f"""
    你是總帥的美股首席戰略官。禁止任何廢話與問候，直接進入「硬核戰報」。
    
    【情報數據】: {json.dumps(data, ensure_ascii=False)}
    【戰略防線】: 
    - VOOG：標普500成長股。戰術：大盤下殺見綠時，手動點射 1 股。
    - MU/NVDA：半導體核心。戰術：獲利保護，死抱不放，無視短期震盪。
    - MU/MUU :的價格比對，例如有無達到MU500的MUU停利點
    
    【戰報結構要求】:
    1. 📡 **美股戰情總結**: 用一句話定調昨日美股盤勢（如：多頭反攻、空頭壓制、高檔震盪）。
    2. 📊 **標的深度透視**: 針對 VOOG, MU, NVDA，列出精確價格，並分析其走勢是否偏離防線。
    3. ⚔️ **今日行動指令**: 
       - 判斷今日開盤是否為「點射時刻」？
       - 針對 NVDA 的持倉給出心理建設，強調「死抱」意志。
       - MU若是跌到350以下需特別提醒，若漲到500以上長效單須取消
    4. 💡 **風險預判**: 簡評今日可能影響市場的宏觀趨勢。
    
    語氣：專業、精確、冷酷。禁止使用軟弱字眼，改用「指令」、「執行」、「埋伏」。
    """
    
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"
    try:
        response = requests.post(api_url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=30)
        report = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        
        full_msg = f"🇺🇸 **【美股晨間硬核戰報 - {tw_time}】**\n{report}"
        # 分段發送確保不截斷
        for i in range(0, len(full_msg), 1900):
            requests.post(DISCORD_URL, json={"content": full_msg[i:i+1900]})
            
        with open("report_us.md", "w", encoding="utf-8") as f: f.write(full_msg)
    except Exception as e:
        print(f"美股分析失敗: {e}")

if __name__ == "__main__": generate_report()
