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
    
    # 【核心升級：法人與防線深度解碼】
    prompt = f"""
    你是總帥的台股戰略副官。禁止開場白，直接進行「法人與防線深度解碼」。
    
    【情報數據】: {json.dumps(data, ensure_ascii=False)}
    【核心戰略防線 - 嚴格監控項目】：
    1. 質押核彈：監控大盤指數（TWII）是否跌破 31,000 點，或 0050 是否跌破 71.2 元。一旦觸發，必須在報告開頭發出「紅燈預警」。
    2. 階梯防禦：當前 0050 每下跌 1.5 元為一個加碼階梯。
    
    
    【戰報結構要求】:
   戰報結構要求】：
    1. 🇹🇼 **台股盤勢掃描**: 簡評今日台股大盤走勢與量能氣氛。
    2. 🕵️ **法人動向偵查**: 
       - 深度解讀「外資、投信、自營商」的買賣超具體數字（以億為單位）。
       - 分析法人集體行為：是撤退、避險，還是暗中佈局？
    3. 🛡️ **防線沙盤推演**: 
       - 根據當前 0050 價格，精確計算距離「71.2 元」質押啟動水位還有多少 % 空間？
       - 根據當前大盤指數，計算距離「31,000 點」核彈門檻還有多少 % 空間？
       - 分析法人今日動向是否對上述防線造成威脅。
    4. ⚔️ **明日預判行動**: 給出明日開盤前的具體戰略部署建議（如：按兵不動、分批掛單、或準備啟動質押資金）。
    
    語氣：冷峻、嚴肅、數據導向。內容要飽滿，必須提到具體的買賣超數字。
    """
    
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"
    try:
        response = requests.post(api_url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=30)
        report = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        
        full_msg = f"🇹🇼 **【台股盤後法人戰報 - {tw_time}】**\n{report}"
        # 分段發送確保不截斷
        for i in range(0, len(full_msg), 1900):
            requests.post(DISCORD_URL, json={"content": full_msg[i:i+1900]})
            
        with open("report_tw.md", "w", encoding="utf-8") as f: f.write(full_msg)
    except Exception as e:
        print(f"台股分析失敗: {e}")

if __name__ == "__main__": generate_report()
