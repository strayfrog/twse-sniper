import yfinance as yf
import json
import time
import requests
import urllib3

# 忽略證交所 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_data():
    # 標的清單
    indices = {"^TWII": "台股加權", "^GSPC": "標普500", "^IXIC": "那斯達克", "^DJI": "道瓊", "^SOX": "費半"}
    tw_list = ["0050", "0056", "00713", "00878", "00915", "00919", "00939", "00940", "00858", "00712", "00931B", "00933B", "00948B", "2330", "2412", "2542", "4306", "2801", "2834", "2845", "2882", "2883", "2885", "2887", "2890", "6005", "6024"]
    us_list = ["NVDA", "MU", "MUU", "UPST", "VZ", "VT", "TLT", "VOOG"]
    
    symbols = list(indices.keys()) + [f"{c}.TW" for c in tw_list] + us_list
    result = {"stocks": {}, "institutional_investors": {}, "metadata": {"UpdateTime": time.strftime("%Y-%m-%d %H:%M:%S")}}

    # A. 抓取股價
    tickers = yf.Tickers(" ".join(symbols))
    for sym in symbols:
        try:
            price = tickers.tickers[sym].fast_info['last_price']
            clean_code = sym.replace(".TW", "")
            result["stocks"][clean_code] = {
                "Price": round(price, 2), 
                "Currency": "USD" if clean_code in us_list else ("PTS" if clean_code in indices else "TWD")
            }
        except: continue

    # B. 抓取台股三大法人買賣超總計
    try:
        resp = requests.get("https://openapi.twse.com.tw/v1/fund/BFI82U", verify=False, timeout=15)
        if resp.status_code == 200:
            for item in resp.json():
                name = item['單位名稱']
                diff_str = item['買賣差額'].replace(",", "")
                diff = int(diff_str)
                result["institutional_investors"][name] = f"{round(diff/100000000, 2)} 億"
    except:
        result["institutional_investors"]["status"] = "法人數據尚未更新"

    with open('stock_data.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    print("🏁 全球情報站數據已更新。")

if __name__ == "__main__":
    fetch_data()
