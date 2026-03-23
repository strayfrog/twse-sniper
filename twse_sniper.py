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

    # A. 證交所全方位火網 (改用 MI_INDEX 收盤行情，這是最準的)
    print("📡 啟動證交所全方位偵蒐...")
    tw_price_map = {}
    
    # 這裡直接呼叫證交所的每日收盤行情大表 (包含 ETF)
    # 00858, 00931B 等都會在這裡
    try:
        # 加上隨機參數避免快取
        url = f"https://www.twse.com.tw/exchangeReport/MI_INDEX?response=json&type=ALL&_={int(time.time())}"
        resp = requests.get(url, timeout=20)
        if resp.status_code == 200:
            data = resp.json()
            # 遍歷資料表，找出符合我們代碼的價格
            # 證交所的 json 格式較複雜，通常在 data9 或 data8
            for key in data.keys():
                if isinstance(data[key], list):
                    for row in data[key]:
                        if len(row) > 8 and row[0] in tw_targets:
                            # row[0] 是代號, row[8] 是收盤價
                            tw_price_map[row[0]] = row[8]
    except Exception as e:
        print(f"⚠️ 證交所主表抓取異常: {e}")

    # B. 判斷是否有漏網之魚，有的話用備援 API
    for code in tw_targets:
        price = tw_price_map.get(code)
        if price and price not in ['-', '0.00', '']:
            result["stocks"][code] = {"Price": float(str(price).replace(",", "")), "Currency": "TWD"}
            print(f"✅ [TWSE] 抓取成功: {code} -> {price}")
        else:
            # 最後的備援：強攻即時行情 API
            try:
                backup_url = f"https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=tse_{code}.tw&_={int(time.time())}"
                b_resp = requests.get(backup_url, timeout=10)
                b_data = b_resp.json()
                # z 是最新成交價, y 是昨日收盤
                p = b_data['msgArray'][0].get('z') or b_data['msgArray'][0].get('y')
                if p and p != '-':
                    result["stocks"][code] = {"Price": float(p), "Currency": "TWD"}
                    print(f"✅ [MIS] 補送成功: {code} -> {p}")
                else:
                    print(f"❌ [FAIL] {code} 依舊無法定位")
            except:
                print(f"❌ [FAIL] {code} 徹底失蹤")

    # C. Yahoo Finance 獲取美股與指數
    print("📡 正在同步美股與指數...")
    for sym in indices_list + us_stocks:
        try:
            ticker = yf.Ticker(sym)
            p = ticker.fast_info['last_price']
            if p:
                name = sym.replace("^", "")
                result["stocks"][name] = {"Price": round(float(p), 2), "Currency": "USD" if sym in us_stocks else "PTS"}
        except: pass

    # D. 法人籌碼
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
