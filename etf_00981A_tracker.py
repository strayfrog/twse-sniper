import pandas as pd
import requests
import os
from datetime import datetime
from io import StringIO

def main():
    url = "https://www.ezmoney.com.tw/ETF/Fund/Info?fundCode=49YTW"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    }
    csv_file = "00981A_holdings.csv"
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 啟動 00981A 偵察任務...")
    
    try:
        res = requests.get(url, headers=headers, timeout=15)
        res.raise_for_status()
        # 強制指定編碼，避免中文字變成亂碼導致 match 失敗
        res.encoding = 'utf-8' 
        
        print("成功取得網頁原始碼，開始掃描表格...")

        # 1. 地毯式搜索：先抓出網頁中所有的表格
        all_tables = pd.read_html(StringIO(res.text))
        print(f"網頁內共偵測到 {len(all_tables)} 個表格，啟動特徵比對...")

        df_target = None
        # 2. 遍歷所有表格，尋找含有「代號」或「名稱」特徵的那個
        for i, df in enumerate(all_tables):
            cols_str = "".join(df.columns.astype(str))
            if "代號" in cols_str or "名稱" in cols_str:
                print(f"🎯 在第 {i+1} 個表格中尋獲持股特徵！")
                df_target = df
                break
        
        if df_target is None:
            # 如果還是找不到，嘗試暴力抓取通常是持股列表的那個位置
            print("⚠️ 未能通過特徵識別表格，嘗試提取首個有效數據表...")
            df_target = all_tables[0]

        # 3. 欄位格式化 (統一欄位名稱)
        df_target = df_target.iloc[:, [0, 1, 2]]
        df_target.columns = ['代號', '名稱', '權重']
        
        # 權重清理 (處理數字後的 % 符號)
        df_target['權重'] = df_target['權重'].astype(str).str.replace('%', '', regex=False).astype(float)
        
        # 4. 歷史紀錄比對
        if os.path.exists(csv_file):
            df_old = pd.read_csv(csv_file)
            # 確保舊資料格式一致
            df_old['權重'] = df_old['權重'].astype(float)
            
            df_merge = pd.merge(df_target, df_old, on=['代號', '名稱'], how='outer', suffixes=('_新', '_舊')).fillna(0)
            df_merge['變化'] = df_merge['權重_新'] - df_merge['權重_舊']
            
            df_changed = df_merge[df_merge['變化'].abs() > 0.05].sort_values(by='變化', ascending=False)
            
            print("\n--- 經理人籌碼變化報告 ---")
            if df_changed.empty:
                print("▶️ 今日無顯著變動。")
            else:
                for _, row in df_changed.iterrows():
                    icon = "🟢 加碼" if row['變化'] > 0 else "🔴 減碼"
                    print(f"{icon} {row['名稱']}: {row['變化']:+.2f}% (現: {row['權重_新']}%)")
        
        # 5. 存檔入庫
        df_target.to_csv(csv_file, index=False, encoding='utf-8-sig')
        print(f"\n✅ 任務成功！數據已存入 {csv_file}")
        
    except Exception as e:
        print(f"\n❌ 偵察任務失敗！錯誤診斷: {str(e)}")

if __name__ == "__main__":
    main()
