import pandas as pd
import requests
import os
from datetime import datetime
from io import StringIO

def main():
    # 🎯 戰略轉進：直接向「台灣證券交易所」要數據
    # 這是 00981A 的官方 PCF (持股組合) 查詢網址，格式極其標準
    twse_url = "https://www.twse.com.tw/exchangeReport/BW01_ETFP_PCF?response=html&etf_id=00981A"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    }
    
    csv_file = "00981A_holdings.csv"
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 啟動【證交所】00981A 數據偵察...")
    
    try:
        # 1. 執行請求
        res = requests.get(twse_url, headers=headers, timeout=25)
        res.raise_for_status()
        res.encoding = 'utf-8' # 證交所通常使用 utf-8
        
        print("📡 已連線至台灣證券交易所數據中心...")

        # 2. 解析 HTML 表格
        # 證交所的表格非常規矩，pandas 可以輕鬆識別
        tables = pd.read_html(StringIO(res.text))
        
        if not tables:
            print("❌ 錯誤：證交所回傳頁面中找不到表格！")
            return

        # 證交所 PCF 表格通常是該頁面的第 3 個表格 (索引 2)
        # 我們用特徵尋找法來確保抓對
        df_new = None
        for t in tables:
            if '股票代碼' in str(t.columns) or '股票代號' in str(t.columns):
                df_new = t
                break
        
        if df_target := df_new is None:
             # 如果沒抓到有 Header 的，就抓最大的那個表格
             df_target = max(tables, key=len)
        else:
             df_target = df_new

        # 3. 數據重組 (證交所欄位: 股票代碼, 股票名稱, 權重)
        # 注意：證交所的欄位順序可能會變，我們採取精準過濾
        try:
            # 找到包含關鍵字的欄位
            col_code = [c for c in df_target.columns if '代碼' in str(c) or '代號' in str(c)][0]
            col_name = [c for c in df_target.columns if '名稱' in str(c)][0]
            col_weight = [c for c in df_target.columns if '權重' in str(c)][0]
            
            df_final = df_target[[col_code, col_name, col_weight]].copy()
            df_final.columns = ['代號', '名稱', '權重']
        except Exception as e:
            print(f"⚠️ 欄位解析失敗，嘗試暴力抓取前三欄: {e}")
            df_final = df_target.iloc[:, [0, 1, 2]]
            df_final.columns = ['代號', '名稱', '權重']

        # 4. 清理數據
        df_final['權重'] = pd.to_numeric(df_final['權重'].astype(str).str.replace('%', ''), errors='coerce')
        df_final = df_final.dropna(subset=['代號']) # 移除非持股列
        
        # 只取前十大 (或是全部保留也可，證交所會給全部)
        df_final = df_final.sort_values(by='權重', ascending=False).head(15)
        print(f"✅ 成功擷取 {len(df_final)} 筆核心持股明細！")

        # 5. 比對與儲存 (保留原本的邏輯)
        if os.path.exists(csv_file):
            try:
                df_old = pd.read_csv(csv_file)
                df_merge = pd.merge(df_final, df_old, on=['代號', '名稱'], how='outer', suffixes=('_新', '_舊')).fillna(0)
                df_merge['變化'] = df_merge['權重_新'] - df_merge['權重_舊']
                df_changed = df_merge[df_merge['變化'].abs() > 0.05].sort_values(by='變化', ascending=False)
                
                print("\n--- 經理人陳釧瑤 籌碼變動偵報 ---")
                if df_changed.empty:
                    print("▶️ 今日持倉極度穩定，無顯著變動。")
                else:
                    for _, row in df_changed.iterrows():
                        icon = "🟢 加碼" if row['變化'] > 0 else "🔴 減碼"
                        print(f"{icon} {row['名稱']}: {row['變化']:+.2f}% (現: {row['權重_新']}%)")
            except:
                pass
        
        df_final.to_csv(csv_file, index=False, encoding='utf-8-sig')
        print(f"💾 歷史檔案已更新：{csv_file}")
        
    except Exception as e:
        print(f"❌ 證交所戰線也遭遇阻礙：{str(e)}")

if __name__ == "__main__":
    main()
