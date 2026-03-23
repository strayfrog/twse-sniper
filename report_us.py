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
    你現在是「首席財富策略總監」。請根據以下的 JSON 盤後/盤前數據，產出今日的【美股晨間戰略報告】。
    
    【絕對紀律與戰略設定】（嚴禁違反，嚴禁給出罐頭理財建議）：
    1. VOO：航空母艦，每月自動定額 $1500 (無視漲跌，作為戰略底盤)。
    2. VOOG (游擊戰)：紀律為「化整為零，慢火點射。買跌不買漲，見綠開槍」。配合 $425 以下分批進場，逢低下殺時手動點射 1 股。
    3. MU (美光)：防守端 GTC 承接網維持 $350 / $340 / $330 不變。攻擊端若 MU 觸發 $500 停利點，必須強力提醒我「全數出清 MUU 轉倉 VOOG」。

    【報告輸出格式】（請用 Markdown 格式，嚴格依照此結構，廢話全免）：
    ### 🎯 美股大盤與重點追蹤
    (簡述 SPY/VOO 的漲跌幅與市場情緒，以及 NVDA, MU 等半導體重心的動向)
    ### 🔫 VOOG 游擊狙擊狀態
    (確認 VOOG 今日是否為綠盤下跌、現價是否低於 $425，判斷是否符合「見綠開槍」的點射條件)
    ### 🚀 MU 網子與轉倉監控
    (回報 MU 距離 $500 轉倉目標，或距離 $350 防守網的差距)
    ### 📋 今晚美股掛單指令
    (給出明確的執行指令：例如「今晚紅盤，封印子彈」、「今晚見綠，建議於 $XXX 附近掛單狙擊 1 股 VOOG」)

    以下是今日全球市場數據：
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
        
    print("🧠 正在呼叫 Gemini 總部進行美股戰略分析...")
    
    report_content = generate_analysis(data)
    
    # 檢查是否為額度耗盡
    if "⚠️ API 額度已耗盡" in report_content:
        print(report_content)
        # 優雅結束，不回傳 exit(1)，讓 Actions 保持綠色
        exit(0)
    elif "❌" not in report_content:
        report_path = "report_us.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# 🇺🇸 每日美股晨間戰略報告\n\n")
            f.write(f"**數據更新時間：** {data.get('metadata', {}).get('UpdateTime', '未知')}\n\n")
            f.write("---\n\n")
            f.write(report_content)
        print(f"✅ 美股戰報產出成功！已儲存至 {report_path}")
    else:
        print(report_content)
        exit(1)
