import os
import json
import requests
import google.generativeai as genai
from datetime import datetime

# --- 1. 安全初始化 ---
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
DISCORD_URL = os.getenv("DISCORD_WEBHOOK_URL")
genai.configure(api_key=GEMINI_KEY)

def send_discord_notify(message):
    payload = {"content": message}
    try:
        r = requests.post(DISCORD_URL, json=payload, timeout=10)
        print(f"Discord 回傳狀態: {r.status_code}")
    except Exception as e:
        print(f"發送失敗: {e}")

def generate_report():
    file_path = 'stock_data.json'
    if not os.path.exists(file_path):
        print("找不到 stock_data.json")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    if not raw_data:
        print("今日數據完全空白，無需報告。")
        return

    # 取得更新時間
    update_time = "未知時間"
    if isinstance(raw_data, list) and len(raw_data) > 0:
        update_time = raw_data[0].get("update_time", datetime.now().strftime('%Y-%m-%d'))
    elif isinstance(raw_data, dict):
        update_time = raw_data.get("update_time", datetime.now().strftime('%Y-%m-%d'))

    # 【🛡️ 總帥 2026 全球資產戰略防線】
    defense_line = """
    * 美股游擊 (VOOG)：三月預算 $3000。戰術：大盤下殺見綠時，手動點射 1 股。
    * 美股防守 (MU / MUU)：產能滿載邏輯不變，續抱。
    * 美股鑽石手 (NVDA)：獲利保護中，死抱不放。
    * 台股階梯防禦 (0050)：動用 25.4 萬。
    """

    # --- 2. 執行 AI 戰略分析 ---
    # 【手術式修正】修正模型名稱路徑
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    你是總帥的首席戰略官。請根據以下數據產出精準、無廢話的「盤後戰報」。
    
    【當前數據】: {json.dumps(raw_data, ensure_ascii=False)}
    【戰略防線】: {defense_line}
    
    【⚠️ 最高軍規鐵律】:
    1. 100% 基於 JSON 數據。若數據中無特定股票價格，請提醒總帥數據未更新。
    2. 嚴禁印出確切持股數量與成本價。
    3. 語氣：專業、冷酷、精確。
    """
    
    try:
        # 額外指定 generation_config 以確保相容性
        response = model.generate_content(prompt)
        report_text = response.text
        # --- 3. 發送戰報 ---
        full_message = f"📡 **【總帥盤後戰報 - {update_time}】**\n{report_text}"
        send_discord_notify(full_message)
    except Exception as e:
        print(f"AI 分析失敗: {e}")

if __name__ == "__main__":
    generate_report()
