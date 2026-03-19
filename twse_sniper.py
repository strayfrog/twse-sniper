import yfinance as yf
import json
import os

def fetch_yfinance_price():
    # 總帥的核心清單
    target_stocks = {
        "2330.TW": "2330",
        "0050.TW": "0050",
        "0056.TW": "0056",
        "00878.TW": "00878",
        "00919.TW": "00919",
        "00929.TW": "00929",
        "00713.TW": "00713"
    }
    
    result = {}
    
    try:
        # 一次性抓取所有標的
        tickers = yf.Tickers(" ".join(target_stocks.keys()))
        
        for symbol, code in target_stocks.items():
            # 抓取最新收盤價
            # yfinance 會自動處理連線與偽裝
            price = tickers.tickers[symbol].fast_info['last_price']
            
            if price:
                result[code] = {
                    "Name": symbol,
                    "ClosingPrice": round(price, 2)
                }
                print(f"✅ 成功抓取 {code}: {price}")
            else:
                print(f"❌ {code} 抓取數值為空")
                
    except Exception as e:
        print(f"❌ yfinance 執行出錯: {e}")

    # 如果沒抓到半個，寫入錯誤
    if not result:
        result = {"status": "error", "message": "yfinance all failed"}

    with open('stock_data.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    fetch_yfinance_price()
