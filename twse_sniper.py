import yfinance as yf
import json
import time
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_data():
    # 1. 定義標的 (確保所有代碼都在清單中)
    indices_list = ["^TWII", "^GSPC", "^IXIC", "^SOX"]
    us_stocks = ["NVDA", "MU", "UPST", "VZ", "VT", "TLT", "VOOG"]
    tw_targets = [
        "0050", "0056", "00713", "00878", "00915", "00919", "00939", "00940", "00712", 
        "2330", "2412", "2542", "4306", "2801", "2834", "2845", "2882", "2883", "2885", 
        "2887", "2890", "6005", "6024", "00858", "00931B", "00933B", "00948B"
    ]
    
    result = {"stocks": {}, "institutional_investors": {}, "metadata": {"UpdateTime": time.strftime("%Y-%m-%d %H:%M:%S")}}

    # A. 證交所多重資料庫偵蒐
    print("📡 啟動證交所 OpenAPI 多維度偵蒐...")
    tw_price_map = {}
    
    # 準備三個不同分類的官方抽屜
    api_sources = [
        "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL", # 一般區
        "https://openapi.twse.com.tw/v1/exchangeReport/BW0648",        # 債券/權證區
        "https://openapi.twse.com.tw/v1/quotation/L_OPEN_DATA"         # 行情匯總區
    ]
    
    for url in api_sources:
        try:
            resp = requests.get(url, timeout=20)
            if resp.status_code == 200:
                data = resp.json()
                for item in data:
                    # 統一欄位名稱判定 (證交所欄位名會變)
                    code = item.get('Code') or item.get('SecuritiesCode') or item.get('證券代號')
                    price = item.get('ClosingPrice') or item.get('收盤價') or item.get('最後揭示價')
                    if code and price and price not in ['-', '0.00', '']:
                        tw_price_map[code] = str(price).replace(",", "")
        except: continue

    # B. 逐一比對標的，若 API 沒抓到，改衝 Yahoo
    for code in tw_targets:
        price = tw_price_map.get(code)
        if price:
            try:
                result["stocks"][code] = {"Price": float(price), "Currency": "TWD"}
                print(f"✅ [TWSE] 抓取成功: {code} -> {price}")
            except: pass
        else:
            print(f"⚠️ [TWSE] 找不到 {code}，切換 Yahoo 備援...")
            try:
                # 嘗試 00931B.TW 或 00858.TW
                ticker_name = f"{code}.TW"
                ticker = yf.Ticker(ticker_name)
                # 先試 fast_info，不行就 history
                p = ticker.fast_info['last_price']
                if p is None or p <= 0:
                    hist = ticker.history(period="1d")
                    if not hist.empty: p = hist['Close'].iloc[-1]
                
                if p:
                    result["stocks"][code] = {"Price": round(float(p), 2), "Currency": "TWD"}
                    print(f"✅ [Yahoo] 抓取成功: {code} -> {p}")
                else:
                    print(f"❌ [FAIL] {code} 徹底失蹤")
            except: pass

    # C. Yahoo Finance 獲取指數與美股
    print("📡 正在同步美股與指數...")
    for sym in indices_list + us_stocks:
        try:
            ticker = yf.Ticker(sym)
            p = ticker.fast_info['last_price']
            if p:
                name = sym.replace("^", "")
                result["stocks"][name] = {"Price": round(float(p), 2), "Currency": "USD" if sym in us_stocks else "PTS"}
        except: pass

    # D. 法人籌碼 (維持原本穩定路徑)
    try:
        f_resp = requests.get("https://www.twse.com.tw/fund/BFI82U?response=json", verify=False, timeout=20)
        f_data = f_resp.json()
        for row in f_data.get('data', []):
            result["institutional_investors"][row[0]] = f"{round(float(row[3].replace(',', '')) / 100000000, 2)} 億"
    except: pass

    # 存檔
    with open('stock_data.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    print("✅ 全球資產戰報數據更新成功。")

if __name__ == "__main__":
    fetch_data()
