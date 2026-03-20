import os
import json
import time
import requests
import yfinance as yf
import google.generativeai as genai
from datetime import datetime

# ==========================================
# 1. 安全金鑰設定 (從 GitHub Secrets 讀取)
# ==========================================
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

if not GOOGLE_API_KEY:
    print("❌ 錯誤：找不到 GEMINI_API_KEY。請確認 GitHub Secrets 已設定，且 yml 檔有 env 掛載。")
    # 測試時若在本地跑，可手動暫時填入，但 Push 前請保持 os.getenv 寫法
    exit(1)

genai.configure(api_key=GOOGLE_API_KEY)

def fetch_data():
    # --- 標的清單 ---
    indices = {"^TWII": "台股加權", "^GSPC": "標普500", "^IXIC": "那斯達克", "^DJI": "道瓊", "^SOX": "費半"}
    # 台股清單 (直接用代碼，不再需要 .TW)
    tw_list = [
        "0050", "0056", "00713", "00878", "00915", "00919", "00939", "00940", 
        "00858", "00712", "00931B", "00933B", "00948B", "2330", "2412", "2542", 
        "4306", "2801", "2834", "2845", "2882", "2883", "2885", "2887", "2890", 
        "6005", "6024"
    ]
    # 美股清單
    us_list = ["NVDA", "MU", "MUU", "UPST", "VZ", "VT", "TLT", "VOO", "VOOG"]

    result = {
        "stocks": {}, 
        "institutional_investors": {}, 
        "metadata": {"UpdateTime": time.strftime("%Y-%m-%d %H:%M:%S")}
    }

    # ==========================================
    # A. 台股數據 (對接證交所 OpenAPI)
    # ==========================================
    print("🚀 正在從 TWSE 證交所抓取台股官方數據...")
    try:
        # 使用每日收盤行情 API (包含 ETF 與 債券 ETF)
        twse_price_url = "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_AVG_ALL"
        tw_resp = requests.get(twse_price_url, timeout=20)
        if tw_resp.status_code == 200:
            tw_all_data = tw_resp.json()
            # 建立快速查詢 Map
            price_map = {item['Code']: item['ClosingPrice'] for item in tw_all_data}
            
            for sid in tw_list:
                price = price_map.get(sid, "N/A")
                result["stocks"][sid] = {"Price": price, "Currency": "TWD"}
        else:
            print(f"⚠️ 台股價格 API 回傳異常: {tw_resp.status_code}")
    except Exception as e:
        print(f"❌ 台股價格抓取失敗: {e}")

    # ==========================================
    # B. 三大法人數據 (對接證交所 OpenAPI)
    # ==========================================
    print("🚀 正在抓取三大法人買賣超...")
    try:
        inst_url = "https://openapi.twse.com.tw/v1/fund/BFI82U_ALL"
        inst_resp = requests.get(inst_url, timeout=15)
        if inst_resp.status_code == 200:
            inst_data = inst_resp.json()
            # 遍歷抓取各類別，並計算總計
            for item in inst_data:
                name = item['Item']
                diff_str = item['BuySellDiff'].replace(",", "")
                billion = round(float(diff_str) / 100000000, 2)
                result["institutional_investors"][name] = f"{billion} 億"
        else:
            result["institutional_investors"]["status"] = "尚未更新"
    except Exception as e:
        result["institutional_investors"]["status"] = f"抓取異常: {str(e)}"

    # ==========================================
    # C. 美股與指數數據 (Yahoo Finance)
    # ==========================================
    print("🚀 正在從 Yahoo Finance 抓取美股與指數...")
    us_symbols = list(indices.keys()) + us_list
    try:
        for sym in us_symbols:
            ticker = yf.Ticker(sym)
            hist = ticker.history(period="1d")
            if not hist.empty:
                last_price = round(hist['Close'].iloc[-1], 2)
                # 清除代碼前綴/後綴供 JSON 顯示
                display_code = sym.replace("^", "")
                result["stocks"][display_code] = {
                    "Price": last_price,
                    "Currency": "USD" if sym in us_list else "PTS"
                }
    except Exception as e:
        print(f"❌ 美股抓取失敗: {e}")

    # ==========================================
    # D. 儲存 JSON 並產出 Markdown 戰報
    # ==========================================
    with open('stock_data.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    print("✅ stock_data.json 更新成功")

    # 呼叫 Gemini 產出戰報
    print("🧠 總監正在產生最終戰報...")
    system_instruction = """
    你是總帥的首席戰略官。請根據數據產出盤後戰報。
    【防線】：VOOG點射、0050階梯防禦、質押預警。
    【格式】：1.情報掃描 2.數據速覽 3.戰術推演。
    【鐵律】：嚴禁印出確切持股數與成本。若休市則回覆今日休市。
    """
    model = genai.GenerativeModel(model_name="gemini-1.5-pro", system_instruction=system_instruction)
    
    # 分別產生台股與美股 MD
    report_tw = model.generate_content(f"台股與籌碼：{json.dumps(result['institutional_investors'], ensure_ascii=False)}")
    with open('report_tw.md', 'w', encoding='utf-8') as f:
        f.write(report_tw.text)
        
    report_us = model.generate_content(f"美股數據：{json.dumps(result['stocks'], ensure_ascii=False)}")
    with open('report_us.md', 'w', encoding='utf-8') as f:
        f.write(report_us.text)

    print("✅ 戰報產出完成。")

if __name__ == "__main__":
    fetch_data()
