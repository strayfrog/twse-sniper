import requests
import json

def fetch_yahoo_finance_price():
    # 總帥的核心觀察名單與對應名稱
    target_stocks = {
        "2330": "台積電",
        "0050": "元大台灣50",
        "0056": "元大高股息",
        "00878": "國泰永續高股息",
        "00919": "群益台灣精選高息",
        "00929": "復華台灣科技優息",
        "00713": "元大台灣高息低波"
    }
    
    # 將代碼轉換為 Yahoo 認識的格式 (加上 .TW)
    symbols = ",".join([f"{code}.TW" for code in target_stocks.keys()])
    # Yahoo 財經底層隱藏版 API
    url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbols}"
    
    # 依然保持最高等級偽裝
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        print("📡 [總監連線中]：正在呼叫 Yahoo Finance 底層 API 獲取最新收盤價...")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        result = {}
        # 拆解 Yahoo 傳回來的資料包
        if "quoteResponse" in data and "result" in data["quoteResponse"]:
            for item in data["quoteResponse"]["result"]:
                # 把 2330.TW 的 .TW 拿掉，還原成純代碼
                code = item["symbol"].replace(".TW", "")
                # 提取最新報價
                price = item.get("regularMarketPrice", 0)
                
                if code in target_stocks:
                    result[code] = {
                        "Name": target_stocks[code],
                        "ClosingPrice": price
                    }
        
        #
