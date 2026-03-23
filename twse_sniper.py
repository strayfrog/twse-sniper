import yfinance as yf
import json
import requests
import urllib3
from datetime import datetime, timezone, timedelta

# 關閉 HTTPS 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_data():
    indices = {"^TWII": "台股加權", "^GSPC": "標普500", "^IXIC": "那斯達克", "^DJI": "道瓊", "^SOX": "費半"}
    tw_list = ["0050", "0056", "00713", "00878", "00915", "00919", "00939", "00940", "00712", "2330", "2412", "2542", "4306", "2801", "2834", "2845", "2882", "2883", "2885", "2887", "2890", "6005", "6024"]
    us_list = ["NVDA", "MU", "MUU", "UPST", "VZ", "VT", "TLT", "VOOG"]
    
    symbols = list(indices.keys()) + [f"{c}.TW" for c in tw_list] + us_list
    result = {"stocks": {}, "institutional_investors": {}, "metadata": {}}
    
    # A. 抓取股價 (yfinance 通常沒問題)
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
            
    # B. 三大法人籌碼 (🚨 回歸官網網址，強化偽裝防護)
    print("📡 正在突擊證交所官網籌碼數據...")
    
    url = "https://www.twse.com.tw/fund/BFI82U?response=json"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://www.twse.com.tw/zh/page/trading/fund/BFI82U.html',
        'Connection': 'keep-alive'
    }

    try:
        # 使用 Session 維持會話狀態
        session = requests.Session()
        # 先打一下網頁版，拿 Cookie
        session.get("https://www.twse.com.tw/zh/page/trading/fund/BFI82U.html", headers=headers, timeout=15)
        # 正式抓取 JSON
        resp = session.get(url, headers=headers, timeout=15)
        
        if resp.status_code == 200:
            raw_data = resp.json()
            if 'data' in raw_data:
                for row in raw_data['data']:
                    name = row[0].strip()
                    diff_str = row[3].replace(",", "")
                    billion = round(float(diff_str) / 100000000, 2)
                    result["institutional_investors"][name] = f"{billion} 億"
            else:
                result["institutional_investors"]["status"] = "今日數據尚未更新"
        else:
            result["institutional_investors"]["status"] = f"官網封鎖中 (HTTP {resp.status_code})"
    except Exception as e:
        result["institutional_investors"]["status"] = f"抓取失敗: {str(e)}"
        
    return result

if __name__ == "__main__":
    data = fetch_data()
    
    # 鎖定台灣時間
    tw_tz = timezone(timedelta(hours=8))
    tw_time_str = datetime.now(tw_tz).strftime("%Y-%m-%d %H:%M:%S")
    
    data["metadata"]["UpdateTime"] = tw_time_str

    with open("stock_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
    print(f"✅ 數據擷取完成！時間：{tw_time_str}")
