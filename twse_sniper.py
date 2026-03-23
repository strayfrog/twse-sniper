import yfinance as yf
import json
import requests
import urllib3
from datetime import datetime, timezone, timedelta

# 關閉不安全的 HTTPS 請求警告 (針對證交所 API)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_data():
    # 標的清單
    indices = {"^TWII": "台股加權", "^GSPC": "標普500", "^IXIC": "那斯達克", "^DJI": "道瓊", "^SOX": "費半"}
    tw_list = ["0050", "0056", "00713", "00878", "00915", "00919", "00939", "00940", "00712", "2330", "2412", "2542", "4306", "2801", "2834", "2845", "2882", "2883", "2885", "2887", "2890", "6005", "6024"]
    us_list = ["NVDA", "MU", "MUU", "UPST", "VZ", "VT", "TLT", "VOOG"]
    
    symbols = list(indices.keys()) + [f"{c}.TW" for c in tw_list] + us_list
    
    result = {"stocks": {}, "institutional_investors": {}, "metadata": {}}
    
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
        except Exception:
            continue
            
    # B. 三大法人籌碼 (切換為穩定路徑 + 偽裝標頭)
    print("📡 正在強制突擊法人籌碼...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        # 使用證交所最新穩定 API 節點
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
        
    # 將整理好的字典回傳
    return result

if __name__ == "__main__":
    # 1. 執行數據抓取
    data = fetch_data()
    
    # 2. 🚨 強制鎖定台灣時間 (UTC+8) 寫入 Metadata
    tw_tz = timezone(timedelta(hours=8))
    tw_time_str = datetime.now(tw_tz).strftime("%Y-%m-%d %H:%M:%S")
    
    if "metadata" not in data:
        data["metadata"] = {}
    data["metadata"]["UpdateTime"] = tw_time_str

    # 3. 儲存 JSON 檔案
    with open("stock_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
    print(f"✅ 全球資產戰報數據更新成功！(更新時間：{tw_time_str})")
