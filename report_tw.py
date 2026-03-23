import os
import json
from google import genai
from google.genai.errors import APIError

def generate_analysis(data):
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return "❌ 錯誤：找不到 GOOGLE_API_KEY 環境變數，無法通訊。"
    
    client = genai.Client(api_key=api_key)
    
    prompt = prompt = f"""
    你現在是「首席財富策略總監」。請根據以下的 JSON 盤後數據，產出今日的【台股盤後戰略報告】。
    
    【絕對紀律與戰略設定】（嚴禁違反，嚴禁給出罐頭理財建議）：
    1. 0050 第一防線 (處分金 25.4 萬階梯防禦)：基準錨點 72.5 元。紀律為「認價不認天，每跌 1.5 元買 1 張」。
       - 具體買點：71.0 元 (1張) -> 69.5 元 (1張) -> 68.0 元 (1張)。
    2. 0050 第二防線 (質押核彈 40 萬，目前尚未動用)：
       - 預警熱機點：大盤跌破 31,000 點或 0050 跌破 71.2 元 (提示執行撥款申請)。
       - 正式開火點：大盤跌破 30,000 點或 0050 跌破 68.0 元 (正式動用質押金，每跌 2 元買 2 張)。
    3. 0050 定期定額：每月 6, 13, 26 日各扣 6,000 元 (無腦執行，僅作為戰略底盤)。
    4. 法人籌碼：根據 `institutional_investors` 買賣超數據，判斷倒貨力道是否會打穿防線。

    【報告輸出格式】（請用 Markdown 格式，嚴格依照此結構，廢話全免）：
    ### 🎯 大盤與籌碼判定
    (簡述今日台股點位與三大法人買賣超，判斷外資與自營商的倒貨力道與市場恐慌程度)
    ### ⚔️ 0050 游擊防線狀態
    (對照目前 0050 價格與 71.0/69.5/68.0 階梯防線的距離，判斷是否觸發買進)
    ### ☢️ 質押核彈啟動判定
    (檢查大盤與 0050 是否逼近預警熱機點 [31000/71.2] 或開火點 [30000/68.0]，並給出明確的「按兵不動」或「啟動」指令)
    ### 📋 明日台股開火指令
    (給出精準的行動總結：例如「防線未破，按兵不動」或「明日開盤掛單 71.0 買入 1 張」)

    以下是今日市場數據：
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
