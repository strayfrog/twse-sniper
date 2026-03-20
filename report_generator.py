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

    # 【時區與時段判定】
    now_tw = datetime.utcnow() + timedelta(hours=8)
    tw_time_str = now_tw.strftime('%Y-%m-%d %H:%M')
    current_hour = now_tw.hour

    # --- 2. 根據時段定制 Prompt ---
    if 7 <= current_hour <= 9:
        # 【早晨 8 點：美股戰場】
        mode = "晨間美股觀測"
        strategic_focus = """
        1. 僅針對 JSON 中的「美股」標的(如 VOOG, MU, NVDA)進行分析。
        2. 檢查昨日美股收盤是否觸發「下殺見綠點射」時機。
        3. 語氣：冷酷的晨間簡報，快速切入重點。
        """
    else:
        # 【下午 4 點：台股與法人戰場】
        mode = "盤後台股分析"
        strategic_focus = """
        1. 針對「台股 0050」與「三大法人買賣超」數據進行深度解析。
        2. 必須提到法人買賣超力道對「25.4 萬防線」的衝擊。
        3. 數據清單不用全秀，僅列出異動最大的關鍵數字。
        """

    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"
    
    prompt = f"""
    你是總帥的首席戰略官。當前任務：【{mode}】。
    
    【情報數據】: {json.dumps(raw_data, ensure_ascii=False)}
    【戰略防線】: VOOG下殺點射、MU/NVDA續抱、0050 25.4萬階梯防禦。
    
    【⚠️ 執行細則】:
    {strategic_focus}
    - 禁止任何開場白。
    - 數據分析後，直接給出「⚔️ 行動建議」。
    - 結尾：回報「報告完畢，請總帥下令。」
    """
    
    try:
        response = requests.post(api_url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=30)
        result = response.json()
        
        if "candidates" in result:
            report_text = result["candidates"][0]["content"]["parts"][0]["text"]
            full_content = f"# 📡 {mode} - {tw_time_str}\n\n{report_text}"
            
            # 存檔與發送
            with open("latest_report.md", "w", encoding="utf-8") as f:
                f.write(full_content)
            send_discord_notify(full_content)
        else:
            print(f"AI 異常: {result}")
            
    except Exception as e:
        print(f"分析失敗: {str(e)}")

if __name__ == "__main__":
    generate_report()
