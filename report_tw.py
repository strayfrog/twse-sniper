import google.generativeai as genai
import os

# 配置 Gemini API
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

def generate_markdown_report(analysis_results):
    """
    使用 Gemini 1.5 Pro 生成台股分析報告
    """
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    prompt = f"""
    你是一位擁有 25 年經驗的「首席財富策略總監」兼「Sniper 戰場傳令兵」。
    請針對以下台股法人籌碼與價位數據進行戰術解讀。
    
    規範：
    1. 嚴禁使用中國大陸用語，一律使用台灣繁體中文術語（如：資訊、籌碼、軟體）。
    2. 針對法人買賣超進行精準判斷。
    3. 嚴禁保證獲利。
    
    數據內容：
    {analysis_results}
    """
    
    try:
        response = model.generate_content(prompt)
        # 核心修正：防禦性檢查 candidates 屬性
        if response and hasattr(response, 'candidates') and len(response.candidates) > 0:
            if response.candidates[0].content.parts:
                return response.text
            else:
                return "分析失敗：回應內容因安全過濾而被封鎖。"
        else:
            return f"分析失敗：模型未回傳有效 candidates。原始回應：{response}"
    except Exception as e:
        return f"台股分析過程發生異常：{str(e)}"

def save_report(report_content, filename="report_tw.md"):
    """
    將報告寫入 Markdown 檔案
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report_content)
        print(f"✅ 台股戰報已成功寫入：{filename}")
    except Exception as e:
        print(f"❌ 檔案寫入失敗：{str(e)}")
