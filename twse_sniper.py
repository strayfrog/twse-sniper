import yfinance as yf
import json
import os
from datetime import datetime
import report_us
import report_tw

# --- 起始關鍵字：def get_stock_data(symbol): ---
def get_stock_data(symbol):
    """
    抓取個股數據，若遇 404 或無數據則自動跳過，避免污染分析內容。
    """
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(period="5d")
        
        # 關鍵診斷：過濾已下市或無效代碼 (解決 404 問題)
        if df.empty or len(df) < 2:
            print(f"⚠️ 標的 {symbol} 數據異常或不存在，已自動跳過。")
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
    確保數據優先寫入，不受後續 AI 分析失敗影響。
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"✅ 數據已成功寫入 {filename}")
    except Exception as e:
        print(f"❌ JSON 儲存失敗: {e}")

if __name__ == "__main__":
    # 這裡放你的標的清單 (建議移除 00858.TW 等確定 404 的代碼)
    target_stocks = ["AAPL", "NVDA", "TSLA", "2330.TW", "0050.TW"] 
    
    all_data = []
    print("📡 開始執行全球資產掃描...")

    for s in target_stocks:
        res = get_stock_data(s)
        if res:
            all_data.append(res)

    # --- 戰術優先執行：先存 JSON，確保 Git Push 有東西可推 ---
    save_to_json(all_data)

    # 準備分析字串
    analysis_results = json.dumps(all_data, ensure_ascii=False)

    # --- 戰略隔離執行：美股與台股互不干擾 ---
    
    # 1. 執行美股分析
    try:
        print("🚀 啟動美股戰略分析...")
        # 確保 report_us.py 已按我之前給你的防禦版本修改
        us_report = report_us.generate_markdown_report(analysis_results)
        report_us.save_report(us_report)
    except Exception as e:
        print(f"❌ 美股分析環節崩潰: {e}")

    # 2. 執行台股分析
    try:
        print("🚀 啟動台股戰術分析...")
        # 確保 report_tw.py 已按我之前給你的防禦版本修改
        tw_report = report_tw.generate_markdown_report(analysis_results)
        report_tw.save_report(tw_report)
