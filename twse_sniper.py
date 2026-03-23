import yfinance as yf
import json
import time
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_data():
    # 1. 精簡後的標的名單 (剔除抓不到的債券 ETF)
    indices_list = ["^TWII", "^GSPC", "^IXIC", "^SOX"]
    us_stocks = ["NVDA", "MU", "UPST", "VZ", "VT", "TLT", "VOOG"]
    tw_targets = [
        "0050", "0056", "00713", "00878", "00915", "00919", "00939", "00940", "00712", 
        "2330", "2412", "2542", "4306", "2801", "2834", "2845", "2882", "2883", "2885", 
        "2887", "2890", "6005", "6024"
    ]
    
    result = {"stocks": {}, "institutional_investors": {}, "metadata": {"UpdateTime": time.strftime("%Y-%m-%d %H:%M:%S")}}

    # A. 證交所個股雷達 (使用最穩定的 STOCK_DAY_ALL)
    print("📡 執行證交所官方數據抓取...")
    try:
        url = "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL"
        resp = requests.get(url, timeout=20)
        if resp.status_code == 200:
            tw_data = resp.json()
            tw_price_map = {item['Code']: item['ClosingPrice'] for item in tw_data}
            for code in tw_targets:
                price = tw_price_map.get(code)
                if price and price not in ['-', '0.00']:
                    result["stocks"][code] = {"Price": float(str(price).replace(",", "")), "Currency": "TWD"}
    except Exception as e:
        print(f"⚠️ 證交所 API 異常: {e}")

    # B. Yahoo Finance 指數與美股
    print("📡 執行 Yahoo Finance 美股與指數抓取...")
    for sym in indices_list + us_stocks:
        try:
            ticker = yf.Ticker(sym)
            # 使用 history 避開 Yahoo 抽風的 fast_info
            hist = ticker.history(period="1d")
            if not hist.empty:
                p = hist['Close'].iloc[-1]
                name = sym.replace("^", "")
                result["stocks"][name] = {"Price": round(float(p), 2), "Currency": "USD" if sym in us_stocks else "PTS"}
        except: pass

    # C. 法人籌碼 (強攻證交所 JSON)
    print("📡 抓取三大法人籌碼...")
    try:
        f_url = "https://www.twse.com.tw/fund/BFI82U?response=json"
        f_resp = requests.get(f_url, verify=False, timeout=20)
        f_data = f_resp.json()
        if 'data' in f_data:
            for row in f_data['data']:
                result["institutional_investors"][row[0]] = f"{round(float(row[3].replace(',', '')) / 100000000, 2)} 億"
    except: pass

    # 4. 存檔 (確保 JSON 格式正確)
    with open('stock_data.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    print("✅ 全球資產戰報數據更新成功。")

if __name__ == "__main__":
    fetch_data()
