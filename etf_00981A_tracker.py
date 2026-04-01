import pandas as pd
import requests
import os
from datetime import datetime
from io import StringIO

def main():
    # 🎯 戰術轉進：Yahoo 奇摩股市 (國際大廠，對 GitHub 機器人最寬容)
    url = "https://tw.stock.yahoo.com/quote/00981A.TW/holding"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    }
    
    csv_file = "00981A_holdings.csv"
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 啟動【Yahoo 奇摩】00981A 偵察任務...")
    
    try:
        res = requests.get(url, headers=headers, timeout=20)
        res.raise_for_status()
        
        # 1. 偵察表格：Yahoo 的特徵是包含「比重」或「持股」
        tables = pd.read_html(StringIO(res.text))
        print(f"📡 網頁掃描完成，發現 {len(tables)} 個表格，啟動特徵比對...")
        
        df_target = None
        for t in tables:
            txt = "".join(t.astype(str).values.flatten())
            if "名稱" in txt and ("比重" in txt or "比例" in txt):
                df_target = t
                break
        
        if df_target is None:
            print("❌ 錯誤：在 Yahoo 頁面中也找不到持股表格！")
            return

        # 2. 數據解剖：Yahoo 的格式通常是 [名稱, 代號, 持股比重]
        # 我們抓取前三欄並重新命名
        df_target = df_target.iloc[:, [0, 1, 2]]
        df_target.columns = ['名稱', '代號', '權重']
        
        # 3. 數據清理
        # Yahoo 的代號有時會黏在名稱裡，或是格式不一，我們進行標準化
        df_target['代號'] = df_target['代號'].astype(str).str.extract('(\d+)')
        df_target['權重'] = pd.to_numeric(df_target['權重'].astype(str).str.replace('%', ''), errors='coerce')
        
        # 移除空值並重新排序
        df_target = df_target.dropna(subset=['代號', '權重']).sort_values(by='權重', ascending=False)
        df_target = df_target[['代號', '名稱', '權重']]
        
        print(f"🎯 成功！擷取到 {len(df_target)} 筆持股資料。")

        # 4. 籌碼變化報告 (與舊資料比對)
        if os.path.exists(csv_file):
            df_old = pd.read_csv(csv_file)
            df_merge = pd.merge(df_target, df_old, on=['代號', '名稱'], how='outer', suffixes=('_新', '_舊')).fillna(0)
            df_merge['變化'] = df_merge['權重_新'] - df_merge['權重_舊']
            
            # 過濾顯著變動
            df_changed = df_merge[df_merge['變化'].abs() > 0.01].sort_values(by='變化', ascending=False)
            
            print("\n" + "="*35 + "\n🕵️‍♂️ 經理人陳釧瑤【今日籌碼動向】\n" + "="*35)
            if df_changed.empty:
                print("▶️ 今日持倉比例極度穩定，無顯著動作。")
            else:
                for _, row in df_changed.iterrows():
                    icon = "🟢 加碼" if row['變化'] > 0 else "🔴 減碼"
                    if row['權重_舊'] == 0: icon = "🆕 新進"
                    elif row['權重_新'] == 0: icon = "🚫 出清"
                    print(f"{icon} {row['名稱']}({row['代號']}): {row['變化']:+.2f}% (現: {row['權重_新']}%)")
            print("="*35)

        # 5. 覆蓋更新 CSV
        df_target.to_csv(csv_file, index=False, encoding='utf-8-sig')
        print(f"💾 歷史檔案已更新：{csv_file}")

    except Exception as e:
        print(f"❌ 偵察任務崩潰：{str(e)}")

if __name__ == "__main__":
    main()
