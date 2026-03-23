import os
import json
from google import genai
from google.genai.errors import APIError

def generate_analysis(data):
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return "❌ 錯誤：找不到 GOOGLE_API_KEY 環境變數，無法通訊。"
    
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    你現在是「首席財富策略總監」。請根據以下的 JSON 盤後數據，產出今日的【台股盤後戰略報告】。
    請嚴格遵守台灣繁體中文術語規範（如：資訊、法人、盤後、籌碼）。

    報告必須包含以下五大結構，並使用 Markdown 格式排版：
    ### I. 現金流與緊急預備金分析
    ### II. 目標量化時程表
    ### III. 投資組合策略表格
    ### IV. 保障規劃優化
    ### V. 下一步行動清單

    以下是今日市場與三大法人籌碼數據：
    ```json
    {json.dumps(data, ensure_ascii=False, indent=2)}
    ```
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text
    except APIError as e:
        # 🚨 關鍵升級：捕捉 API 錯誤，特別是 429 額度耗盡
        if e.code == 429:
            return "⚠️ API 額度已耗盡 (429 Resource Exhausted)，跳過本次戰報產出。"
        return f"❌ AI 通訊錯誤：{e.message}"
    except Exception as e:
        return f"❌ 未知分析失敗：{e}"

if __name__ == "__main__":
    json_path = "stock_data.json"
    
    if not os.path.exists(json_path):
        print(f"❌ 找不到數據檔 {json_path}，無法產出戰報。")
        exit(1)
        
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    print("🧠 正在呼叫 Gemini 總部進行台股戰略分析...")
    
    report_content = generate_analysis(data)
    
    # 檢查是否為額度耗盡
    if "⚠️ API 額度已耗盡" in report_content:
        print(report_content)
        # 優雅結束，不回傳 exit(1)，讓 Actions 保持綠色
        exit(0)
    elif "❌" not in report_content:
        report_path = "report_tw.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# 🇹🇼 每日台股盤後戰略報告\n\n")
            f.write(f"**數據更新時間：** {data.get('metadata', {}).get('UpdateTime', '未知')}\n\n")
            f.write("---\n\n")
            f.write(report_content)
        print(f"✅ 台股戰報產出成功！已儲存至 {report_path}")
    else:
        print(report_content)
        exit(1)
