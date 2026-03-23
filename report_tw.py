import google.generativeai as genai
import os
import json

def generate_analysis(data):
    """
    使用 Gemini 1.5 Flash 分析台股數據
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "錯誤: 找不到 GEMINI_API_KEY 環境變數"

    genai.configure(api_key=api_key)
    
    # 設定安全性過濾器，避免財經數據分析被誤判攔截
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
    你是一位專業的台股分析師。請根據以下 JSON 格式的股票數據（包含技術指標、法人籌碼與盤後資訊），
    提供一份精簡且專業的中文分析報告。
    報告必須包含：
    1. 整體盤勢總結。
    2. 值得關注的強勢個股與原因。
    3. 潛在風險提示。
    
    數據內容：
    {json.dumps(data, ensure_ascii=False, indent=2)}
    """

    try:
        response = model.generate_content(prompt)
        # 檢查是否有正常回傳內容
        if response and response.text:
            return response.text
        else:
            return "Gemini 回傳了空結果，可能是內容觸發了過濾機制。"
    except Exception as e:
        return f"台股分析執行失敗: {str(e)}"

if __name__ == "__main__":
    # 測試程式邏輯用
    pass
