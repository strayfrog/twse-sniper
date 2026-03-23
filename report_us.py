import google.generativeai as genai
import os
import json

def generate_analysis(data):
    """
    使用 Gemini 1.5 Flash 分析美股數據
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "錯誤: 找不到 GEMINI_API_KEY 環境變數"

    genai.configure(api_key=api_key)
    
    # 設定安全性過濾器
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]

    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        safety_settings=safety_settings
    )
    
    prompt = f"""
    你是一位專業的美股投資專家。請分析以下提供的美股市場數據 JSON，
    產出一份針對專業投資者的分析報告。
    請特別專注於技術面走勢與關鍵支撐壓力位。
    
    數據內容：
    {json.dumps(data, ensure_ascii=False, indent=2)}
    """

    try:
        response = model.generate_content(prompt)
        if response and response.text:
            return response.text
        else:
            return "Gemini 未能產生美股分析內容。"
    except Exception as e:
        return f"美股分析執行失敗: {str(e)}"

if __name__ == "__main__":
    pass
