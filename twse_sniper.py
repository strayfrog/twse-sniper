import requests
import json
import time

def fetch_yahoo_price():
    target_stocks = {
        "2330": "台積電", "0050": "元大台灣50", "0056": "元大高股息",
        "00878": "國泰永續高股息", "00919": "群益台灣精選高息",
        "00929": "復華台灣科技優息", "00713": "元大台灣高息低波"
    }
    
    symbols = ",".join([f"{code}.TW" for code in target_stocks.keys()])
    url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbols}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,ame/apng,*/*;q=0.8",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    
    result = {}
    for attempt in range(3): # 最多嘗試 3 次
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if "quoteResponse" in data and "result" in data["quoteResponse"]:
                for item in data["quoteResponse"]["result"]:
                    code = item["symbol"].replace(".TW", "")
                    price = item.get("regularMarketPrice")
                    if code in target_stocks and price:
                        result[code] = {
                            "Name": target_stocks[code],
                            "ClosingPrice": price,
                            "UpdateTime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                        }
            if result: break # 抓到資料就跳出循環
        except Exception as e:
            print(f"嘗試 {attempt+1} 失敗: {e}")
            time.sleep(2) # 失敗後停 2 秒再試
            
    # 如果最終還是失敗，寫入錯誤訊息
    if not result:
        result = {"status": "error", "message": "All attempts failed"}

    with open('stock_data.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    print("✅ 處理完成")

if __name__ == "__main__":
    fetch_yahoo_price()
