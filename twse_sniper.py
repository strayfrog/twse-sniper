import requests
import re
import json

def fetch_google_price():
    # 核心代碼：TPE 代表台北證券交易所
    target_stocks = {
        "2330": "TPE:2330", "0050": "TPE:0050", "0056": "TPE:0056",
        "00878": "TPE:00878", "00919": "TPE:00919", "00929": "TPE:00929", "00713": "TPE:00713"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "zh-TW,zh;q=0.9"
    }
    
    result = {}
    
    for code, full_code in target_stocks.items():
        url = f"https://www.google.com/finance/quote/{full_code}"
        try:
            response = requests.get(url, headers=headers, timeout=10)
            # 使用正則表達式直接從網頁 HTML 中抓取價格數字
            # Google Finance 的價格通常放在 data-last-price 這個屬性裡
            match = re.search(r'data-last-price="([\d\.]+)"', response.text)
            
            if match:
                price = match.group(1)
                result[code] = {
                    "Name": full_code,
                    "ClosingPrice": price
                }
                print(f"✅ 已抓取 {code}: {price}")
            else:
                print(f"❌ 無法在網頁中找到 {code} 的價格")
                
        except Exception as e:
            print(f"❌ 抓取 {code} 發生錯誤: {e}")

    # 最終寫入檔案
    if not result:
        result = {"status": "error", "message": "Google Finance scraping failed"}

    with open('stock_data.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    fetch_google_price()
