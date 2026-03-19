import requests
import json
import os

def fetch_core_holdings_price():
    url = "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_AVG_ALL"
    target_stocks = ["2330", "0050", "0056", "00878", "00919", "00929", "00713"]
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        result = {}
        for item in data:
            if item.get("Code") in target_stocks:
                result[item.get("Code")] = {
                    "Name": item.get("Name"),
                    "ClosingPrice": item.get("ClosingPrice")
                }
        
        # 將抓到的報價寫入一個乾淨的 JSON 檔案中
        with open('stock_data.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
            
        print("✅ 數據已成功寫入 stock_data.json")
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")

if __name__ == "__main__":
    fetch_core_holdings_price()
