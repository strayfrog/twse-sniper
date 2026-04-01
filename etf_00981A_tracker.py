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
        # 1. 向 Google 衛星請求情報
        res = requests.get(SECRET_CSV_URL, timeout=20)
        res.raise_for_status()
        # 強制指定編碼為 utf-8 避免中文字亂碼
        res.encoding = 'utf-8'
        
        # 2. 讀取 CSV 數據
        # 由於 MoneyDJ 抓下來的表格通常帶有標題列，我們直接讀取
        df_raw = pd.read_csv(StringIO(res.text))
        print(f"✅ 衛星連線成功，接收到 {len(df_raw)} 筆原始數據。")

        # 3. 數據精煉 (抓取：持股名稱、比例%、代號)
        # 備註：Google 抓下來的欄位名稱可能包含「持股名稱」、「比例(%)」、「代碼」
        # 我們採位置定位法 [0, 1, 2] 避免欄位名稱變動
        df_new = df_raw.iloc[:, [0, 1, 2]].copy()
        df_new.columns = ['名稱', '比例', '代碼']
        
        # 清理數據：將比例轉為數字，提取純數字代號
        df_new['代號'] = df_new['代碼'].astype(str).str.extract('(\d+)')
        df_new['權重'] = pd.to_numeric(df_new['比例'].astype(str).str.replace('%', ''), errors='coerce')
        
        # 最終格式整理
        df_final = df_new[['代號', '名稱', '權重']].dropna(subset=['代號', '權重']).sort_values(by='權重', ascending=False)
        print(f"📊 數據精煉完成，目前有效持股共 {len(df_final)} 檔。")

        # 4. 歷史籌碼變動分析 (比對 Repo 裡的舊 CSV)
        if os.path.exists(csv_file):
            df_old = pd.read_csv(csv_file)
            df_old['權重'] = df_old['權重'].astype(float)
            
            # 合併新舊資料進行比對
            df_merge = pd.merge(df_final, df_old, on=['代號', '名稱'], how='outer', suffixes=('_新', '_舊')).fillna(0)
            df_merge['變化'] = df_merge['權重_新'] - df_merge['權重_舊']
            
            # 篩選有意義的變動 (> 0.01%)
            df_changed = df_merge[df_merge['變化'].abs() > 0.01].sort_values(by='變化', ascending=False)
            
            print("\n" + "="*35)
            print("🕵️‍♂️ 經理人陳釧瑤【持倉變動情報】")
            print("="*35)
            if df_changed.empty:
                print("▶️ 今日持倉極度穩定，經理人按兵不動。")
            else:
                for _, row in df_changed.iterrows():
                    # 判斷動作類型
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

        # 5. 覆蓋存檔 (供 GitHub Actions 提交)
        df_final.to_csv(csv_file, index=False, encoding='utf-8-sig')
        print(f"\n💾 任務成功！情報已寫入資料庫：{csv_file}")

    except Exception as e:
        print(f"\n❌ 衛星偵察發生故障：{str(e)}")
        print("💡 請確認 Google Sheets 是否已「發布到網路」並選擇「CSV」格式。")

if __name__ == "__main__":
    main()
