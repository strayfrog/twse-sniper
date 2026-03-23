import yfinance as yf
import json
import os
from datetime import datetime
import report_us
import report_tw

def get_stock_data(symbol):
    """
    抓取個股數據，若遇 404 或無數據則自動跳過。
    """
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(period="5d")
        
        if df.empty or len(df) < 2:
            print(f"⚠️ 標的 {symbol} 數據異常，已跳過。")
            return None
            
        current_price = df['Close'].iloc[-1]
        prev_price = df['Close'].iloc[-2]
        change_pct = ((current_price / prev_price) - 1) * 100
        
        return {
            "symbol": symbol,
            "price": round(current_price, 2),
            "change": f"{round(change_pct, 2)}%",
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        print(f"❌ 抓取 {symbol} 失敗: {str(e)}")
        return None

def save_to_json(data, filename="stock.json"):
    """
    確保數據優先寫入。
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"✅ 數據已寫入 {filename}")
    except Exception as e:
        print(f"❌ JSON 儲存失敗: {e}")

if __name__ == "__main__":
    # 建議在此移除 00858.TW 等無效標的
    target_stocks = ["AAPL", "NVDA", "TSLA", "2330.TW", "0050.TW"] 
    
    all_data = []
    print("📡 開始執行全球資產掃描...")

    for s in target_stocks:
        res = get_stock_data(s)
        if res:
            all_data.append(res)

    # 1. 先存 JSON (數據優先)
    save_to_json(all_data)
    analysis_results = json.dumps(all_data, ensure_ascii=False)

    # --- 戰略隔離執行區塊：嚴格對齊 try-except ---
    
    # 2. 執行美股分析
    try:
        print("🚀 啟動美股戰略分析...")
        us_report = report_us.generate_markdown_report(analysis_results)
        report_us.save_report(us_report)
    except Exception as e:
        print(f"❌ 美股分析失敗: {e}")

    # 3. 執行台股分析
    try:
        print("🚀 啟動台股戰術分析...")
        tw_report = report_tw.generate_markdown_report(analysis_results)
        report_tw.save_report(tw_report)
    except Exception as e:
        print(f"❌ 台股分析失敗: {e}")

    print("🏁 全球資產戰報任務執行完畢。")
