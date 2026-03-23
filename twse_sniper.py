import yfinance as yf
import json
import time
import requests
import urllib3

# 停用不安全的請求警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_data():
    # 1. 標的名單精簡：移除導致系統異常的債券型 ETF，確保數據穩定
    indices_list = ["^TWII", "^GSPC", "^IXIC", "^SOX"]
    us_stocks = ["NVDA", "MU", "UPST", "VZ", "VT", "TLT", "VOOG"]
    tw_targets = [
        "0050", "0056", "00713", "00878", "00915", "00919", "00939", "00940", "00712", 
        "2330", "2412", "2542", "4306", "2801", "2834", "2845", "2882", "2883", "2885", 
        "2887", "2890", "6005", "6024"
    ]
    
    result = {
        "stocks": {}, 
        "institutional_investors": {}, 
        "metadata": {"UpdateTime": time.strftime("%Y-%m-%d %H:%M:%S")}
    }

    # A. 證交所官方 API 數據偵蒐
    print("📡 啟動證交所 OpenAPI 數據同步...")
    try:
        url = "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL"
        resp = requests.get(url, timeout=20)
        if resp.status_code == 200:
            tw_data = resp.json()
            # 建立代碼與價格的對照表
            tw_price_map = {item['Code']: item['ClosingPrice'] for item in tw_data}
            for code in tw_targets:
                price = tw_price_map.get(code)
                if price and price not in ['-', '0.00']:
                    result["stocks"][code] = {
                        "Price": float(str(price).replace(",", "")),
                        "Currency": "TWD"
                    }
    except Exception as e:
        print(f"⚠️ 證交所 API 異常：{e}")

    # B. Yahoo Finance 獲取指數與美股數據
    print("📡 啟動 Yahoo Finance 數據抓取...")
    for sym in indices_list + us_stocks:
        try:
            ticker = yf.Ticker(sym)
            # 使用歷程記錄確保數據獲取成功
            hist = ticker.history(period="1d")
            if not hist.empty:
                p = hist['Close'].iloc[-1]
                name = sym.replace("^", "")
                result["stocks"][name] = {
                    "Price": round(float(p), 2),
                    "Currency": "USD" if sym in us_stocks else "PTS"
                }
        except:
            pass

    # C. 三大法人籌碼數據
    print("📡 抓取法人籌碼資訊...")
    try:
        f_url = "https://www.twse.com.tw/fund/BFI82U?response=json"
        f_resp = requests.get(f_url, verify=False, timeout=20)
        f_data = f_resp.json()
        if 'data' in f_data:
            for row in f_data['data']:
                # row[0] 為法人名稱, row[3] 為買賣超金額
                result["institutional_investors"][row[0]] = f"{round(float(row[3].replace(',', '')) / 100000000, 2)} 億"
    except:
        pass

    # 4. 儲存戰報 JSON 檔案
    with open('stock_data.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    print("✅ 全球資產數據同步完成。")

if __name__ == "__main__":
    fetch_data()
