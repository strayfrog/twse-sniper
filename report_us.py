import google.generativeai as genai
import os

genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

def generate_markdown_report(analysis_results):
    model = genai.GenerativeModel('gemini-1.5-pro')
    prompt = f"你是首席財富策略總監，請針對以下美股數據提供戰略分析，嚴禁大陸用語：\n{analysis_results}"
    try:
        response = model.generate_content(prompt)
        # 防禦性檢查 candidates
        if hasattr(response, 'candidates') and len(response.candidates) > 0:
            return response.text
        else:
            return f"美股分析失敗：API 未回傳內容。原始回應：{response}"
    except Exception as e:
        return f"美股分析過程發生異常：{str(e)}"

def save_report(report_content, filename="report_us.md"):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report_content)
        print(f"✅ 美股戰報已成功寫入：{filename}")
    except Exception as e:
        print(f"❌ 美股檔案寫入失敗：{str(e)}")
