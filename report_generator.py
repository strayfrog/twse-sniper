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
    
    # 【🛡️ 總帥 2026 全球資產戰略防線】
    defense_line = """
    * 美股游擊 (VOOG)：下殺見綠時點射。
    * 美股防守 (MU / MUU)：續抱，無視震盪。
    * 美股鑽石手 (NVDA)：獲利保護，死抱不放。
    * 台股階梯防禦 (0050)：25.4 萬防線，每跌 1% 考慮動用部分資金。
    """

    # --- 2. 執行 AI 戰略分析 (強化 Prompt 版) ---
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    
    # 【核心升級：深度分析指令】
    prompt = f"""
    你是總帥的首席軍事戰略官，請針對以下數據進行「硬核分析」：
    
    【當前情報】: {json.dumps(raw_data, ensure_ascii=False)}
    【戰略防線】: {defense_line}
    
    【⚠️ 戰報格式要求】:
    1. 📡 **戰情總結**: 一句話評論今日大盤氣氛。
    2. 📊 **數據透視**: 針對 JSON 內的標的，列出價格變化並評註。
    3. ⚔️ **行動建議**: 結合「戰略防線」，具體建議現在該「點射」、「死抱」還是「動用防禦資金」。
    4. 語氣：精確、冷酷、充滿軍事威嚴。禁止廢話。
    """
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 1000,
            "temperature": 0.8  # 略微調高創造性，讓分析更有見地
        }
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        result = response.json()
        
        if "candidates" in result:
            report_text = result["candidates"][0]["content"]["parts"][0]["text"]
            full_message = f"📡 **【總帥盤後硬核戰報 - {update_time}】**\n{report_text}"
            send_discord_notify(full_message)
        else:
            print(f"AI 異常: {json.dumps(result)}")
            
    except Exception as e:
        print(f"分析崩潰: {str(e)}")

if __name__ == "__main__":
    generate_report()
