import yfinance as yf
import json
import time
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_data():
    # 1. 定義標的
    indices_list = ["^TWII", "^GSPC", "^IXIC", "^SOX"]
    us_stocks = ["NVDA", "MU", "UPST", "VZ", "VT", "TLT", "VOOG"]
    
    # 這是您要監控的所有台股/債券代號 (不需要加 .TW)
    tw_targets = [
        "0050", "0056", "00713", "00878", "00915", "00919", "00939", "00940", "00712", 
        "2330", "2412", "2542", "4306", "2801", "2834", "2845", "2882", "2883", "2885", 
        "2887", "2890", "6005", "6024", "00858", "00931B", "00933B", "00948B"
    ]
    
    result = {
        "stocks": {}, 
        "institutional_investors": {}, 
        "metadata": {"UpdateTime": time.strftime("%Y-%m-%d %H:%M:%S")}
    }

    # A. 第一波：突擊證交所 OpenAPI (取得所有台股價格)
    print("📡 正在從證交所 OpenAPI 獲取台股最新報價...")
    try:
        # 這個 API 會回傳當日所有上市股票的成交資訊
        twse_url = "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL"
        resp = requests.get(twse_url, timeout=30)
        if resp.status_code == 200:
            all_tw_data = resp.json()
            # 將資料轉為 dict 方便查詢
            tw_price_map = {item['Code']: item['ClosingPrice'] for item in all_tw_data}
            
            for code in tw_targets:
                price = tw_price_map.get(code)
                if price and price != '0.00':
                    result["stocks"][code] = {
                        "Price": float(price.replace(",", "")),
                        "Currency": "TWD"
                    }
                else:
                    print(f"⚠️ 證交所 API 找不到 {code} 或今日無交易")
        else:
            print(f"❌ 證交所 API 請求失敗: {resp.status_code}")
    except Exception as e:
        print(f"❌ 證交所 API 連線異常: {e}")

    # B. 第二波：從 Yahoo Finance 獲取大盤指數與美股
    print("📡 正在從 Yahoo Finance 獲取美股與指數...")
    yf_symbols = indices_list + us_stocks
    for sym in yf_symbols:
        try:
            ticker = yf.Ticker(sym)
            # 指數用 fast_info, 美股用 history 確保精準
            price = ticker.fast_info['last_price']
            if price is None or price <= 0:
                hist = ticker.history(period="1d")
                if not hist.empty:
                    price = hist['Close'].iloc[-1]
            
            if price:
                clean_name = sym.replace("^", "")
                result["stocks"][clean_name] = {
                    "Price": round(float(price), 2),
                    "Currency": "USD" if sym in us_stocks else "PTS"
                }
        except Exception as e:
            print(f"❌ Yahoo 抓取 {sym} 失敗: {e}")

    # C. 第三波：三大法人籌碼 (維持原本穩定路徑)
    print("📡 正在獲取法人籌碼...")
    try:
        fund_url = "https://www.twse.com.tw/fund/BFI82U?response=json"
        f_resp = requests.get(fund_url, verify=False, timeout=20)
        if f_resp.status_code == 200:
            f_data = f_resp.json()
            for row in f_data.get('data', []):
                name = row[0]
                billion = round(float(row[3].replace(",", "")) / 100000000, 2)
                result["institutional_investors"][name] = f"{billion} 億"
    except:
        result["institutional_investors"]["status"] = "籌碼抓取失敗"

    # 存檔
    with open('stock_data.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    print("✅ 全球資產戰報數據更新成功 (證交所 API 版)。")

if __name__ == "__main__":
    fetch_data()
