import yfinance as yf
import json
import time
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_data():
    # 1. 標的分組偵蒐
    indices = {"^TWII": "台股加權", "^GSPC": "標普500", "^IXIC": "那斯達克", "^SOX": "費半"}
    
    # 普通台股/一般 ETF
    tw_common = ["0050", "0056", "00713", "00878", "00915", "00919", "00939", "00940", "00712", "2330", "2412", "2542", "4306", "2801", "2834", "2845", "2882", "2883", "2885", "2887", "2890", "6005", "6024"]
    
    # 債券型 ETF (必須帶 B)
    tw_bonds = ["00858", "00931B", "00933B", "00948B"] 
    
    # 美股
    us_list = ["NVDA", "MU", "UPST", "VZ", "VT", "TLT", "VOOG"]

    # 彙整所有 Yahoo 認得的代碼
    symbols = list(indices.keys()) + [f"{c}.TW" for c in tw_common] + [f"{c}.TW" for c in tw_bonds] + us_list
    
    result = {
        "stocks": {}, 
        "institutional_investors": {}, 
        "metadata": {"UpdateTime": time.strftime("%Y-%m-%d %H:%M:%S")}
    }

    # A. 抓取股價 (強化容錯版)
    print("📡 正在同步台美股價...")
    for sym in symbols:
        try:
            ticker = yf.Ticker(sym)
            # 使用 fast_info 或 history 取最後一筆，增加穩定性
            price = ticker.fast_info['last_price']
            
            # 如果抓不到(None)，嘗試用 history 補位
            if price is None or price <= 0:
                hist = ticker.history(period="1d")
                if not hist.empty:
                    price = hist['Close'].iloc[-1]
            
            clean_code = sym.replace(".TW", "")
            if price:
                result["stocks"][clean_code] = {
                    "Price": round(float(price), 2),
                    "Currency": "USD" if sym in us_list else ("PTS" if sym in indices else "TWD")
                }
            else:
                print(f"⚠️ 無法取得 {sym} 的即時數據，跳過。")
        except Exception as e:
            print(f"❌ 抓取 {sym} 失敗: {str(e)}")
            continue

    # B. 三大法人 (維持您的穩定路徑)
    print("📡 正在強制突擊法人籌碼...")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    try:
        url = "https://www.twse.com.tw/fund/BFI82U?response=json"
        resp = requests.get(url, headers=headers, verify=False, timeout=20)
        if resp.status_code == 200:
            data = resp.json()
            if 'data' in data:
                for row in data['data']:
                    name = row[0]
                    diff_str = row[3].replace(",", "")
                    billion = round(float(diff_str) / 100000000, 2)
                    result["institutional_investors"][name] = f"{billion} 億"
            else:
                result["institutional_investors"]["status"] = "證交所尚未開牌"
        else:
            result["institutional_investors"]["status"] = f"連線受阻 ({resp.status_code})"
    except Exception as e:
        result["institutional_investors"]["status"] = f"偵巡異常: {str(e)}"

    # C. 存檔
    with open('stock_data.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    print("✅ 全球資產戰報數據更新成功。")

if __name__ == "__main__":
    fetch_data()
