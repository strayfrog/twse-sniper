import pandas as pd
import requests
import os
from datetime import datetime
from io import StringIO

def main():
    # 🎯 戰略目標：MoneyDJ 的 00981A 持股明細頁面
    url = "https://www.moneydj.com/ETF/X/Basic/Basic0007B.xdjhtm?etfid=00981A.TW"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    }
    
    csv_file = "00981A_holdings.csv"
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 啟動【MoneyDJ】00981A 偵察任務...")
    
    try:
        # 1. 取得網頁 HTML
        res = requests.get(url, headers=headers, timeout=20)
        res.raise_for_status()
        res.encoding = 'utf-8' # MoneyDJ 的 XDJHTM 頁面通常使用 utf-8
        
        # 2. 解析表格
        # MoneyDJ 的表格通常包含「持股名稱」這個字眼
        tables = pd.read_html(StringIO(res.text), match='持股名稱')
        
        if not tables:
            print("❌ 錯誤：在 MoneyDJ 頁面中找不到持股表格。")
            return

        df_target = tables[0]
        print(f"🎯 成功定位持股表格，共有 {len(df_target)} 筆資料。")

        # 3. 數據清理
        # MoneyDJ 欄位通常是：持股名稱、比例(%)、代碼 (有時順序會變)
        # 我們利用關鍵字自動對應欄位
        cols = df_target.columns.tolist()
        col_name = [c for c in cols if '名稱' in str(c)][0]
        col_code = [c for c in cols if '代號' in str(c) or '代碼' in str(c)][0]
        col_weight = [c for c in cols if '比例' in str(c) or '權重' in str(c)][0]
        
        df_final = df_target[[col_code, col_name, col_weight]].copy()
        df_final.columns = ['代號', '名稱', '權重']
        
        # 清理權重 (移除 % 符號並轉為數字)
        df_final['權重'] = pd.to_numeric(df_final['權重'].astype(str).str.replace('%', ''), errors='coerce')
        # 移除權重為 NaN 或 0 的無效列
        df_final = df_final[df_final['權重'] > 0].sort_values(by='權重', ascending=False)
        
        # 4. 歷史比對
        if os.path.exists(csv_file):
            try:
                df_old = pd.read_csv(csv_file)
                df_merge = pd.merge(df_final, df_old, on=['代號', '名稱'], how='outer', suffixes=('_新', '_舊')).fillna(0)
                df_merge['變化'] = df_merge['權重_新'] - df_merge['權重_舊']
                df_changed = df_merge[df_merge['變化'].abs() > 0.01].sort_values(by='變化', ascending=False)
                
                print("\n" + "="*30)
                print("🕵️‍♂️ 經理人陳釧瑤【持倉變動追蹤】")
                print("="*30)
                if df_changed.empty:
                    print("▶️ 今日持倉穩定，無顯著變動。")
                else:
                    for _, row in df_changed.iterrows():
                        icon = "🟢 加碼" if row['變化'] > 0 else "🔴 減碼"
                        if row['權重_舊'] == 0: icon = "🆕 新進"
                        elif row['權重_新'] == 0: icon = "🚫 出清"
                        print(f"{icon} {row['名稱']}({row['代號']}): {row['變化']:+.2f}% (現: {row['權重_新']}%)")
                print("="*30)
            except Exception as e:
                print(f"⚠️ 比對引擎異常: {e}")

        # 5. 存檔
        df_final.to_csv(csv_file, index=False, encoding='utf-8-sig')
        print(f"\n✅ 任務成功！最新情報已同步至 {csv_file}")

    except Exception as e:
        print(f"❌ MoneyDJ 偵察失敗：{str(e)}")

if __name__ == "__main__":
    main()
