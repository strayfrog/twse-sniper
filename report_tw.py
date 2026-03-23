import google.generativeai as genai
import json
import os
import requests

def generate_report():
    # 讀取數據 (加入錯誤處理)
    try:
        with open('stock_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        stocks = data.get('stocks', {})
        inst = data.get('institutional_investors', {})
    except Exception as e:
        print(f"數據讀取失敗: {e}")
        return

    # 設定 Gemini 與安全門檻 (解決 candidates 報錯的關鍵)
    genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]

    # 專業提示詞 (強制執行台灣用語)
    prompt = f"""
    你是首席財富策略總監。請分析以下台股盤後數據並撰寫戰報。
    規範：嚴禁使用中國大陸用語，必須使用台灣繁體中文標準術語。
    
    【今日數據】
    台股大盤: {stocks.get('TWII', {}).get('Price', 'N/A')}
    台積電: {stocks.get('2330', {}).get('Price', 'N/A')}
    三大法人籌碼: {json.dumps(inst, ensure_ascii=False)}
    其他監控標的: {json.dumps(stocks, ensure_ascii=False)}
    """

    try:
        response = model.generate_content(prompt, safety_settings=safety_settings)
        if response.candidates:
            content = response.text
            with open('report_tw.md', 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ 台股報告同步完成")
            # 發送 Discord
            webhook = os.environ.get('DISCORD_WEBHOOK_URL')
            if webhook: requests.post(webhook, json={"content": content})
    except Exception as e:
        print(f"分析失敗: {e}")

if __name__ == "__main__":
    generate_report()
