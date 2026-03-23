import yfinance as yf
import json
import time
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_data():
    indices_list = ["^TWII", "^GSPC", "^IXIC", "^SOX"]
    us_stocks = ["NVDA", "MU", "UPST", "VZ", "VT", "TLT", "VOOG"]
    tw_targets = [
        "0050", "0056", "00713", "00878", "00915", "00919", "00939", "00940", "00712", 
        "2330", "2412", "2542", "4306", "2801", "2834", "2845", "2882", "2883", "2885", 
        "2887", "2890", "6005", "6024", "00858", "00931B", "00933B", "00948B"
    ]
    
    result = {"stocks": {}, "institutional_investors": {}, "metadata": {"UpdateTime": time.strftime("%Y-%m-%d %H:%M:%S")}}

    # A. 證交所雙雷達偵蒐 (一般股 + 債券/權證區)
    print("📡 啟動證交所 OpenAPI 雙軌偵蒐...")
    tw_price_map = {}
    urls = [
        "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL", # 一般個股
        "https://openapi.twse.com.tw/v1/exchangeReport/BW0648"        # 債券型/其他
    ]
    
    for url in urls:
        try:
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                for item in data:
                    # 抓取 Code (代碼) 與 ClosingPrice (收盤價)
                    code = item.get('Code') or item.get('SecuritiesCode')
                    price = item.get('ClosingPrice')
                    if code and price:
                        tw_price_map[code] = price
        except: continue

    for code in tw_targets:
        price = tw_price_map.get(code)
        if price and price != '0.00' and price != '-':
            result["stocks"][code] = {"Price": float(price.replace(",", "")), "Currency": "TWD"}
        else:
            print(f"⚠️ 證交所 API 仍找不到 {code}，嘗試備援方案...")
            # 備援：若官方 API 還是沒有，最後試一次 Yahoo
            try:
                ticker = yf.Ticker(f"{code}.TW")
                p = ticker.fast_info['last_price']
                if p: result["stocks"][code] = {"Price": round(float(p), 2), "Currency": "TWD"}
            except: pass

    # B. Yahoo Finance 獲取指數與美股
    print("📡 正在獲取美股與指數...")
    for sym in indices_list + us_stocks:
        try:
            ticker = yf.Ticker(sym)
            p = ticker.fast_info['last_price']
            if p:
                name = sym.replace("^", "")
                result["stocks"][name] = {"Price": round(float(p), 2), "Currency": "USD" if sym in us_stocks else "PTS"}
        except: pass

    # C. 法人籌碼
    try:
        f_resp = requests.get("https://www.twse.com.tw/fund/BFI82U?response=json", verify=False, timeout=20)
        f_data = f_resp.json()
        for row in f_data.get('data', []):
            result["institutional_investors"][row[0]] = f"{round(float(row[3].replace(',', '')) / 100000000, 2)} 億"
    except: pass

    with open('stock_data.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    print("✅ 全球資產戰報數據更新成功。")

if __name__ == "__main__":
    fetch_data()
