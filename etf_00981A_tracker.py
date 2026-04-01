import pandas as pd
import os
import requests
from datetime import datetime
from io import StringIO

def main():
    # 🎯 您的專屬 Google 衛星 CSV 連結
    SECRET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSqouCKETlhac1mao4vp73voRKgc_FDiPyAwNCL9waAyRMt6KESu-SQp2lDFjsJ32jAFM65TM9gx0P5/pub?output=csv"
    
    csv_file = "00981A_holdings.csv"
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 啟動【Google 衛星】00981A 偵察任務...")
    
    try:
        res = requests.get(SECRET_CSV_URL, timeout=20)
        res.raise_for_status()
        res.encoding = 'utf-8'
        
        df_raw = pd.read_csv(StringIO(res.text))
        print(f"✅ 衛星連線成功，接收到 {len(df_raw)} 筆原始數據。")

        # --- 🛠️ 戰術升級：精準解剖代號與名稱 ---
        # 提取前兩欄：[0]是名稱(含代號), [1]是比例
        df_new = df_raw.iloc[:, [0, 1]].copy()
        df_new.columns = ['原始名稱', '比例']
        
        # 1. 抓取代號：從 "台積電(2330.TW)" 中把 2330 挖出來，並強制轉為「字串(str)」防止 0 消失
        df_new['代號'] = df_new['原始名稱'].str.extract(r'\(([A-Za-z0-9]+)\.TW\)').astype(str)
        # 處理沒有 .TW 的情況 (萬一格式變動)
        df_new['代號'] = df_new['代號'].replace('nan', pd.NA)
        df_new['代號'] = df_new['代號'].fillna(df_new['原始名稱'].str.extract(r'\(([A-Za-z0-9]+)\)')[0]).astype(str)
        
        # 2. 清理名稱：把括號和裡面的代號都切掉，只留 "台積電"
        df_new['名稱'] = df_new['原始名稱'].str.replace(r'\(.*?\)', '', regex=True).str.strip()
        
        # 3. 轉換權重
        df_new['權重'] = pd.to_numeric(df_new['比例'].astype(str).str.replace('%', ''), errors='coerce')
        
        # 整理為最終格式
        df_final = df_new[['代號', '名稱', '權重']].dropna(subset=['代號', '權重']).sort_values(by='權重', ascending=False)
        print(f"📊 數據精煉完成，目前有效持股共 {len(df_final)} 檔。")

        # --- 歷史籌碼變動分析 ---
        if os.path.exists(csv_file):
            # 🛡️ 關鍵防禦：讀取昨天的 CSV 時，強制規定「代號」是字串 (str)
            df_old = pd.read_csv(csv_file, dtype={'代號': str})
            df_old['權重'] = df_old['權重'].astype(float)
            
            df_merge = pd.merge(df_final, df_old, on=['代號', '名稱'], how='outer', suffixes=('_新', '_舊')).fillna(0)
            df_merge['變化'] = df_merge['權重_新'] - df_merge['權重_舊']
            
            df_changed = df_merge[df_merge['變化'].abs() > 0.01].sort_values(by='變化', ascending=False)
            
            print("\n" + "="*35)
            print("🕵️‍♂️ 經理人陳釧瑤【持倉變動情報】")
            print("="*35)
            if df_changed.empty:
                print("▶️ 今日持倉極度穩定，經理人按兵不動。")
            else:
                for _, row in df_changed.iterrows():
                    if row['權重_舊'] == 0:
                        status = "🆕 新進"
                    elif row['權重_新'] == 0:
                        status = "🚫 出清"
                    elif row['變化'] > 0:
                        status = "🟢 加碼"
                    else:
                        status = "🔴 減碼"
                        
                    print(f"{status} {row['名稱']}({row['代號']}): {row['變化']:+.2f}% (現: {row['權重_新']}%)")
            print("="*35)
        else:
            print("\n⚠️ 偵察兵初次建檔，歷史對比功能將於明日啟動。")

        # 5. 存檔入庫
        df_final.to_csv(csv_file, index=False, encoding='utf-8-sig')
        print(f"\n💾 任務成功！情報已精確寫入：{csv_file}")

    except Exception as e:
        print(f"\n❌ 衛星偵察發生故障：{str(e)}")

if __name__ == "__main__":
    main()
