import google.generativeai as genai
import json
import os
import requests

def generate_report():
    try:
        with open('stock_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        stocks = data.get('stocks', {})
        inst = data.get('institutional_investors', {})
    except Exception as e:
        print(f"讀取數據失敗: {e}")
        return

    genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # 這是破解 'candidates' 報錯的唯一密碼
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]

    prompt = f"""
    你是首席財富策略總監。請分析以下台股數據。
    規範：嚴禁使用中國大陸用語，必須使用台灣繁體中文專業術語（如：資訊、軟體、硬碟）。
    數據：{json.dumps(data, ensure_ascii=False)}
    """

    try:
        response = model.generate_content(prompt, safety_settings=safety_settings)
        if response.text:
            with open('report_tw.md', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("✅ 台股戰報產出成功")
            webhook = os.environ.get('DISCORD_WEBHOOK_URL')
            if webhook: requests.post(webhook, json={"content": response.text})
    except Exception as e:
        print(f"分析官拒絕簽署: {e}")

if __name__ == "__main__":
    generate_report()
