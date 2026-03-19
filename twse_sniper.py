import yfinance as yf
import json
import time
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_data():
    indices = {"^TWII": "台股加權", "^GSPC": "標普500", "^IXIC": "那斯達克", "^DJI": "道瓊", "^SOX": "費半"}
    tw_list = ["0050", "0056", "00713", "00878", "00915", "00919", "00939", "00940", "00858", "00712", "00931B", "00933B", "00948B", "2330", "2412", "2542", "4306", "2801", "2834", "2845", "2882", "2883", "2885", "2887", "2890", "6005", "6024"]
    us_list = ["NVDA", "MU", "MUU", "UPST", "VZ", "VT", "TLT", "VOOG"]
    
    symbols = list(indices.keys()) + [f"{c}.TW" for c in tw_list] + us_list
    result = {"stocks": {}, "institutional_investors": {}, "metadata": {"UpdateTime": time.strftime("%Y-%m-%d %H:%M:%S")}}

    # A. 股價抓取
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

    # B. 三大法人 (精準對接 BFI82U 節點)
    try:
        # 官方節點：三大法人買賣金額統計
        resp = requests.get("https://openapi.twse.com.tw/v1/fund/BFI82U", verify=False, timeout=20)
        
        if resp.status_code == 200:
            raw_data = resp.json()
            # 官方 JSON 鍵值：'Item' (單位名稱), 'Difference' (買賣差額)
            for entry in raw_data:
                label = entry.get('Item', '')
                # 濾掉逗號並轉為數字
                diff_str = entry.get('Difference', '0').replace(",", "")
                try:
                    billion = round(float(diff_str) / 100000000, 2)
                    result["institutional_investors"][label] = f"{billion} 億"
                except:
                    continue
        else:
            result["institutional_investors"]["status"] = f"API 連線失敗: {resp.status_code}"
    except Exception as e:
        result["institutional_investors"]["status"] = f"抓取異常: {str(e)}"

    with open('stock_data.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    print("✅ 全球資產與法人籌碼同步更新完成。")

if __name__ == "__main__":
    fetch_data()
