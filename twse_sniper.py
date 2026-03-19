import yfinance as yf
import json
import time

def fetch_inventory_prices():
    # 🌟 根據總帥 Keep「2026 全球資產配置總清單」自動同步
    # 台股清單 (自動加上 .TW)
    tw_assets = {
        "0050": "元大台灣50", "0056": "元大高股息", "00713": "元大台灣高息低波", 
        "00878": "國泰永續高股息", "00915": "凱基優選高股息", "00919": "群益台灣精選高息", 
        "00939": "統一台灣高息動能", "00940": "元大台灣價值高息", "00858": "永豐美國500大",
        "00712": "復華富時不動產", "00931B": "元大美債20年", "00933B": "國泰10Y+金融債", 
        "00948B": "中信上游半導體債", "2330": "台積電", "2412": "中華電", 
        "2542": "興富發", "4306": "炎洲", "2801": "彰銀", "2834": "臺企銀", 
        "2845": "遠東銀", "2882": "國泰金", "2883": "開發金", "2885": "元大金", 
        "2887": "台新金", "2890": "永豐金", "6005": "群益證", "6024": "群益期"
    }
    
    # 美股清單 (直接代碼)
    us_assets = {
        "NVDA": "輝達", "MU": "美光", "MUU": "兩倍做多MU", "UPST": "Upstart", 
        "VZ": "威瑞森", "VT": "全股市ETF", "TLT": "美債20年ETF", "VOOG": "標普500成長股"
    }
    
    # 合併清單
    all_symbols = [f"{c}.TW" for c in tw_assets.keys()] + list(us_assets.keys())
    
    result = {}
    print(f"📡 [總部雷達] 開始偵巡全球共 {len(all_symbols)} 檔資產...")
    
    try:
        # 一次性調用資料庫
        tickers = yf.Tickers(" ".join(all_symbols))
        
        for sym in all_symbols:
            try:
                # 取得最新價格
                price = tickers.tickers[sym].fast_info['last_price']
                clean_code = sym.replace(".TW", "")
                
                # 獲取正確名稱
                name = tw_assets.get(clean_code) or us_assets.get(clean_code)
                
                if price:
                    result[clean_code] = {
                        "Name": name,
                        "Price": round(price, 2),
                        "Currency": "TWD" if ".TW" in sym else "USD",
                        "UpdateTime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    }
            except Exception:
                continue # 個別失敗則跳過，確保主進程不中斷

    except Exception as e:
        result = {"status": "error", "message": str(e)}

    # 寫入 JSON
    with open('stock_data.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    print(f"✅ [偵巡結束] 已成功更新 {len(result)} 檔資產狀態。")

if __name__ == "__main__":
    fetch_inventory_prices()
