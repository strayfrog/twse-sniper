import pandas as pd
import requests
import os
from datetime import datetime

# ==========================================
# 00981A 籌碼情報偵察兵 (純寫入 CSV 版)
# ==========================================

def main():
    url = "https://www.ezmoney.com.tw/ETF/Fund/Info?fundCode=49YTW"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    csv_file = "00981A_holdings.csv"
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 啟動 00981A 籌碼偵察任務...")
    
    try:
        # 1. 抓取今日最新資料
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        tables = pd.read_html(res.text)
        
        # 抓取表格前三欄：代號、名稱、權重
        df_new = tables[0].iloc[:, [0, 1, 2]]
        df_new.columns = ['代號', '名稱', '權重']
        
        # 清除 % 符號並轉為數字
        df_new['權重'] = df_new['權重'].astype(str).str.replace('%', '', regex=False).astype(float)
        
        # 2. 比對昨日資料 (僅印出在 GitHub Log 供除錯與紀錄參考)
        if os.path.exists(csv_file):
            df_old = pd.read_csv(csv_file)
            df_merge = pd.merge(df_new, df_old, on=['代號', '名稱'], how='outer', suffixes=('_新', '_舊')).fillna(0)
            df_merge['變化'] = df_merge['權重_新'] - df_merge['權重_舊']
            
            df_changed = df_merge[df_merge['變化'].abs() > 0.05].sort_values(by='變化', ascending=False)
            
            print("\n--- 經理人籌碼變化 (變化 > 0.05%) ---")
            if df_changed.empty:
                print("▶️ 今日前十大持股無顯著變動，經理人按兵不動。")
            else:
                for _, row in df_changed.iterrows():
                    icon = "🟢 加碼" if row['變化'] > 0 else "🔴 減碼"
                    print(f"{icon} {row['名稱']}: {row['變化']:+.2f}% (現: {row['權重_新']}%)")
        else:
            print("\n⚠️ 找不到舊檔案，今日將建立初始 CSV 資料庫。")
            
        # 3. 覆蓋存檔，準備讓 YAML 排程執行 git commit
        df_new.to_csv(csv_file, index=False, encoding='utf-8-sig')
        print(f"\n✅ 任務成功！最新持股已更新至 {csv_file}")
        
    except Exception as e:
        print(f"\n❌ 偵察任務失敗：網頁結構可能已更改，或遭到伺服器阻擋。")
        print(f"錯誤訊息: {str(e)[:200]}")

if __name__ == "__main__":
    main()
