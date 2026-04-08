import pandas as pd
import os
import requests
from datetime import datetime
from io import StringIO

def main():
    # 🎯 您的專屬 Google 衛星 CSV 連結
    SECRET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSqouCKETlhac1mao4vp73voRKgc_FDiPyAwNCL9waAyRMt6KESu-SQp2lDFjsJ32jAFM65TM9gx0P5/pub?output=csv"
    
    csv_file = "00981A_holdings.csv"
    today_str = datetime.now().strftime('%Y-%m-%d')
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 啟動【Google 衛星 V2】00981A 偵察任務...")
    
    try:
        # 1. 抓取最新原始數據
        res = requests.get(SECRET_CSV_URL, timeout=20)
        res.raise_for_status()
        res.encoding = 'utf-8'
        
        df_raw = pd.read_csv(StringIO(res.text))
        print(f"✅ 衛星連線成功，接收到 {len(df_raw)} 筆原始數據。")

        # 2. 清理今日數據
        df_new = df_raw.iloc[:, [0, 1]].copy()
        df_new.columns = ['原始名稱', '比例']
        
        # 萃取代號與名稱
        df_new['代號'] = df_new['原始名稱'].str.extract(r'\(([A-Za-z0-9]+)\.TW\)').astype(str)
        df_new['代號'] = df_new['代號'].replace('nan', pd.NA)
        df_new['代號'] = df_new['代號'].fillna(df_new['原始名稱'].str.extract(r'\(([A-Za-z0-9]+)\)')[0]).astype(str)
        df_new['名稱'] = df_new['原始名稱'].str.replace(r'\(.*?\)', '', regex=True).str.strip()
        df_new['權重'] = pd.to_numeric(df_new['比例'].astype(str).str.replace('%', ''), errors='coerce')
        
        # 建立今日基準表 (新增日期欄位)
        df_today = df_new[['代號', '名稱', '權重']].dropna(subset=['代號', '權重']).copy()
        df_today.insert(0, '日期', today_str) # 確保日期在第一欄
        
        print(f"📊 數據精煉完成，今日有效持股共 {len(df_today)} 檔。")

        # 3. 讀取歷史檔案並進行疊加
        if os.path.exists(csv_file):
            # 讀取舊檔案 (強制代號為字串)
            df_history = pd.read_csv(csv_file, dtype={'代號': str})
            
            # 【關鍵】如果舊檔案沒有「日期」欄位 (第一次升級 V2)，手動補上假日期以免出錯
            if '日期' not in df_history.columns:
                 df_history.insert(0, '日期', '2026-04-07') # 預設給一個舊日期
                 
            # 【防呆】如果今天已經跑過這個腳本了，先把今天的舊資料刪掉，免得重複疊加
            df_history = df_history[df_history['日期'] != today_str]
            
            # 把今天的資料「往下疊加 (Append)」到歷史資料庫中
            df_final = pd.concat([df_history, df_today], ignore_index=True)
            
        else:
            # 如果是全新的檔案，直接把今天的資料當成最終資料
            print("\n⚠️ 這是第一次執行，直接建立全新資料庫。")
            df_final = df_today

        # 4. 寫回 CSV (覆蓋原檔，但內容是疊加後的)
        # 確保順序乾淨：日期, 代號, 名稱, 權重
        df_final = df_final[['日期', '代號', '名稱', '權重']]
        df_final.to_csv(csv_file, index=False, encoding='utf-8-sig')
        print(f"\n💾 任務成功！歷史軌跡與今日變動已完美寫入單一資料庫：{csv_file}")

    except Exception as e:
        print(f"\n❌ 衛星偵察發生故障：{str(e)}")

if __name__ == "__main__":
    main()
