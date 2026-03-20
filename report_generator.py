import os
import json
import requests
from google import genai
from datetime import datetime

# --- 1. 安全初始化 ---
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
DISCORD_URL = os.getenv("DISCORD_WEBHOOK_URL")

# 使用最簡化的客戶端宣告
client = genai.Client(api_key=GEMINI_KEY)

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

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
    except Exception as e:
        print(f"讀取 JSON 失敗: {e}")
        return

    update_time = datetime.now().strftime('%Y-%m-%d %H:%M')

    # 【🛡️ 總帥 2026 全球資產戰略防線】
    defense_line = """
    * 美股游擊 (VOOG)：下殺見綠時點射。
    * 美股防守 (MU / MUU)：續抱。
    * 美股鑽石手 (NVDA)：死抱不放。
    * 台股階梯防禦 (0050)：25.4 萬防線。
    """

    # --- 2. 執行 AI 戰略分析 ---
    try:
        # 【核心修正】強制使用最簡短的 ID，不加任何前綴
        model_id = "gemini-1.5-flash" 
        
        prompt = f"你是總帥首席戰略官。請根據數據產出精簡戰報：{json.dumps(raw_data, ensure_ascii=False)}\n戰略防線：{defense_line}"
        
        # 移除 contents 以外的所有參數，確保相容性
        response = client.models.generate_content(
            model=model_id,
            contents=prompt
        )
        
        report_text = response.text
        full_message = f"📡 **【總帥盤後戰報 - {update_time}】**\n{report_text}"
        send_discord_notify(full_message)
        
    except Exception as e:
        # 印出完整的錯誤詳細資訊，如果是 404，我們會看到它到底在找哪個路徑
        print(f"AI 分析失敗詳情: {str(e)}")

if __name__ == "__main__":
    generate_report()
