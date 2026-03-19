import yfinance as yf
import json
import time

def fetch_complete_global_intelligence():
    # 🌟 1. 指數雷達 (台股 + 美股四大指數)
    indices = {
        "^TWII": "台股加權指數",
        "^GSPC": "標普500指數",
        "^IXIC": "那斯達克指數",
        "^DJI": "道瓊工業指數",
        "^SOX": "費城半導體指數"
    }

    # 🌟 2. 根據總帥 Keep「2026 全球資產配置總清單」同步之持股
    # 台股清單
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
    
    # 美股持股
    us_assets = {
        "NVDA": "輝達", "MU": "美光", "MUU": "兩倍做多MU", "UPST": "Upstart", 
        "VZ": "威瑞森", "VT": "全股市ETF", "TLT": "美債20年ETF", "VOOG": "標普500成長股"
    }
    
    all_symbols = list(indices.keys()) + [f"{c}.TW" for c in tw_assets.keys()] + list(us_assets.keys())
    
    result = {}
    print(f"📡 [總部連線] 全面偵巡台美大盤及 {len(all_symbols)-5} 檔核心資產...")
    
    try:
        tickers = yf.Tickers(" ".join(all_symbols))
        
        for sym in all_symbols:
            try:
                price = tickers.tickers[sym].fast_info['last_price']
                clean_code = sym.replace(".TW", "")
                name = indices.get(clean_code) or tw_assets.get(clean_code) or us_assets.get(clean_code)
                
                if price:
                    if sym in indices:
                        category = "INDEX"
                        currency =
