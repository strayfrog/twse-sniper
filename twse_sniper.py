import yfinance as yf
import json
import time
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_data():
    # 標的清單
    indices = {"^TWII": "台股加權", "^GSPC": "標普500", "^IXIC": "那斯達克", "^DJI": "道瓊", "^SOX": "費半"}
    tw_list = ["0050", "0056", "00713", "00878", "00915", "00919", "00939", "00940", "00858.TW", "00712", "00931B.TW", "00933B.TW", "00948B.TW", "2330", "2412", "2542", "4306", "2801", "2834", "2845", "2882", "2883", "2885", "2887", "2890", "6005", "6024"]
    us_list = ["NVDA", "MU", "MUU", "UPST", "VZ", "VT", "TLT", "VOOG"]
    
    symbols = list(indices.keys()) + [f"{c}.TW" for c in tw_list] + us_list
    result = {"stocks": {}, "institutional_investors": {}, "metadata": {"UpdateTime": time.strftime("%Y-%m-%d %H:%M:%S")}}

    # A. 抓取股價
    print("📡 正在同步台美股價...")
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

    # B. 三大法人 (切換為穩定路徑 + 偽裝標頭)
    print("📡 正在強制突擊法人籌碼...")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    try:
        # 改用這個節點，資料格式最穩定
        url = "https://www.twse.com.tw/fund/BFI82U?response=json"
        resp = requests.get(url, headers=headers, verify=False, timeout=20)
        
        if resp.status_code == 200:
            data = resp.json()
            # 格式解析：data['data'] 是一個列表，每一項是 [單位名稱, 買進, 賣出, 差額]
            if 'data' in data:
                for row in data['data']:
                    name = row[0]
                    diff_str = row[3].replace(",", "")
                    billion = round(float(diff_str) / 100000000, 2)
                    result["institutional_investors"][name] = f"{billion} 億"
            else:
                result["institutional_investors"]["status"] = "證交所尚未開牌"
        else:
            result["institutional_investors"]["status"] = f"連線受阻 (Code: {resp.status_code})"
    except Exception as e:
        result["institutional_investors"]["status"] = f"偵巡異常: {str(e)}"

    with open('stock_data.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    print("✅ 全球資產戰報數據更新成功。")

if __name__ == "__main__":
    fetch_data()
