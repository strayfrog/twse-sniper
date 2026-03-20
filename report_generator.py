import os
import json
import requests
from datetime import datetime

# --- 1. 安全初始化 ---
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
DISCORD_URL = os.getenv("DISCORD_WEBHOOK_URL")

def send_discord_notify(message):
    # Discord 穩定上限約 2000，我們留緩衝
    if len(message) > 1900:
        message = message[:1800] + "\n\n(⚠️ 因通訊限制，後續內容已略過)"
        
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
    
    # --- 2. 執行 AI 戰略分析 ---
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    
    # 【核心修正】加入「字數限制」與「格式限制」指令
    prompt = f"""
    你是總帥的首席戰略官。請根據以下數據進行「硬核分析」。
    
    【當前情報】: {json.dumps(raw_data, ensure_ascii=False)}
    【戰略防線】: VOOG 買綠不買紅、MU/NVDA 續抱、0050 25.4萬階梯防禦。
    
    【⚠️ 格式鐵律】:
    1. 限制在「600 字內」完成。
    2. 禁止使用過多層級的 Markdown 表格。
    3. 必須包含：📡戰情總結、📊數據透視、⚔️行動建議。
    4. 結尾必須加上「報告完畢，請下令。」以示連線完整。
    """
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 1000, # 減少最大輸出防止爆掉
            "temperature": 0.6
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
