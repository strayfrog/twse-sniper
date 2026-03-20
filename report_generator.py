import os
import json
import requests
from google import genai
from datetime import datetime

# --- 1. 安全初始化 ---
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
DISCORD_URL = os.getenv("DISCORD_WEBHOOK_URL")

# 【核心修正 1】強制指定使用 v1 穩定版 API，避開 v1beta 坑洞
client = genai.Client(api_key=GEMINI_KEY, http_options={'api_version': 'v1'})

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

    update_time = datetime.now().strftime('%Y-%m-%d %H:%M')

    # 【🛡️ 總帥 2026 全球資產戰略防線】
    defense_line = """
    * 美股游擊 (VOOG)：三月預算 $3000。下殺見綠時點射。
    * 美股防守 (MU / MUU)：續抱無視震盪。
    * 美股鑽石手 (NVDA)：獲利保護，死抱不放。
    * 台股階梯防禦 (0050)：動用 25.4 萬。
    """

    # --- 2. 執行 AI 戰略分析 ---
    try:
        prompt = f"你是總帥首席戰略官。請根據數據產出戰報：{json.dumps(raw_data, ensure_ascii=False)}\n戰略防線：{defense_line}"
        
        # 【核心修正 2】直接使用最簡潔的模型名稱
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=prompt
        )
        
        report_text = response.text
        full_message = f"📡 **【總帥盤後戰報 - {update_time}】**\n{report_text}"
        send_discord_notify(full_message)
        
    except Exception as e:
        print(f"AI 分析失敗: {str(e)}")

if __name__ == "__main__":
    generate_report()
