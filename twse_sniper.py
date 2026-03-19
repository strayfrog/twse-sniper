import yfinance as yf
import json
import time
import requests
import urllib3

# 1. 忽略證交所憑證警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_data():
    # 標的清單 (對接您的 Keep 資產配置清單)
    indices = {"^TWII": "台股加權", "^GSPC": "標普500", "^IXIC": "那斯達克", "^DJI": "道瓊", "^SOX": "費半"}
    tw_list = ["0050", "0056", "00713", "00878", "00915", "00919", "00939", "00940", "00858", "00712", "00931B", "00933B", "00948B", "2330", "2412", "2542", "4306", "2801", "2834", "2845", "2882", "2883", "2885", "2887", "2890", "6005", "6024"]
    us_list = ["NVDA", "MU", "MUU", "UPST", "VZ", "VT", "TLT", "VOOG"]
    
    symbols = list(indices.keys()) + [f"{c}.TW" for c in tw_list] + us_list
    result = {
        "stocks": {}, 
        "institutional_investors": {}, 
        "metadata": {"UpdateTime": time.strftime("%Y-%m-%d %H:%M:%S")}
    }

    # A. 抓取股價 (yfinance)
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

    # B. 三大法人精準對接 (針對 BFI82U 節點)
    print("📡 正在同步三大法人籌碼數據...")
    try:
        # 證交所 OpenAPI 節點
        resp = requests.get("https://openapi.twse.com.tw/v1/fund/BFI82U", verify=False, timeout=15)
        
        if resp.status_code == 200:
            data = resp.json()
            # 遍歷資料，精準提取關鍵欄位
            for item in data:
                # 取得單位名稱 (Item) 與 買賣差額 (Difference)
                name = item.get('Item') or item.get('單位名稱')
                diff_str = item.get('Difference') or item.get('買賣差額')
                
                if name and diff_str:
                    # 去除逗號並轉為億元單位
                    try:
                        diff_num = float(diff_str.replace(",", ""))
                        result["institutional_investors"][name] = f"{round(diff_num / 100000000, 2)} 億"
                    except:
                        continue
            
            # 若成功抓取但資料為空 (可能當日休市)
            if not result["institutional_investors"]:
                result["institutional_investors"]["status"] = "今日休市或尚未開牌"
        else:
            result["institutional_investors"]["status"] = f"API 連線異常 (代碼: {resp.status_code})"
            
    except Exception as e:
        # 將錯誤詳細資訊寫入 JSON 方便偵錯
        result["institutional_investors"]["status"] = f"抓取異常: {str(e)}"

    # 寫入檔案
    with open('stock_data.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    print(f"🏁 情報站更新完成。")

if __name__ == "__main__":
    fetch_data()
