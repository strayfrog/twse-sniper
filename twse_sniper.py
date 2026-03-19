import requests
import json
import os
import urllib3

# 關閉煩人的 SSL 警告訊息
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_core_holdings_price():
    url = "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_AVG_ALL"
    target_stocks = ["2330", "0050", "0056", "00878", "00919", "00929", "00713"]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        # 🌟 關鍵突破：加入 verify=False，無視證交所破爛的 SSL 憑證，強制連線！
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        response.raise_for_status()
        data = response.json()
        
        result = {}
        for item in data:
            if item.get("Code") in target_stocks:
                result[item.get("Code")] = {
                    "Name": item.get("Name"),
                    "ClosingPrice": item.get("ClosingPrice")
                }
        
        with open('stock_data.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
            
        print("✅ 數據已成功抓取並寫入 stock_data.json")
        
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
        with open('stock_data.json', 'w', encoding='utf-8') as f:
            json.dump({"status": "error", "message": str(e)}, f)

if __name__ == "__main__":
    fetch_core_holdings_price()
