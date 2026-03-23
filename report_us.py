import google.generativeai as genai
import json
import os
import requests

def generate_report():
    try:
        with open('stock_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        stocks = data.get('stocks', {})
    except: return

    genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]

    prompt = f"""
    你是首席財富策略總監。請分析以下美股與全球數據。
    規範：嚴禁使用中國大陸用語，必須使用台灣繁體中文標準術語。
    數據：{json.dumps(stocks, ensure_ascii=False)}
    """

    try:
        response = model.generate_content(prompt, safety_settings=safety_settings)
        if response.candidates:
            content = response.text
            with open('report_us.md', 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ 美股報告同步完成")
            webhook = os.environ.get('DISCORD_WEBHOOK_URL')
            if webhook: requests.post(webhook, json={"content": content})
    except Exception as e:
        print(f"分析失敗: {e}")

if __name__ == "__main__":
    generate_report()
