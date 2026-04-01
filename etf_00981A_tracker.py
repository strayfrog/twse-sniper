import pandas as pd
import requests
import os
from datetime import datetime
from io import StringIO

def main():
    # 🎯 戰術目標：玩股網 (WantGoo) - 數據相對好抓
    url = "https://www.wantgoo.com/stock/etf/00981A/constituent"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Referer": "https://www.wantgoo.com/",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    
    csv_file = "00981A_holdings.csv"
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 啟動【玩股網】00981A 偵察任務...")
    
    try:
        # 1. 取得網頁原始碼
        res = requests.get(url, headers=headers, timeout=20)
        
        # 🛡️ 偵察紀錄：看伺服器回傳什麼
        print(f"📡 伺服器回應代碼: {res.status_code}")
        if res.status_code == 403:
            print("❌ 慘了！GitHub 的 IP 真的被玩股網封鎖了 (403 Forbidden)。")
            return
            
        # 2. 解析表格 (指定 match '權重' 來過濾)
        try:
            tables = pd.read_html(StringIO(res.text), match='權重')
            print(f"✅ 成功定位表格！偵測到 {len(tables)} 個目標。")
            df_target = tables[0]
        except Exception as e:
            print(f"❌ 解析表格失敗：{e}")
            print("--- 網頁內容片段 (前500字) ---")
            print(res.text[:500])
            return

        # 3. 數據清理 (玩股網欄位通常是：代碼, 名稱, 權重...)
        # 我們自動尋找包含關鍵字的欄位位置
        cols = df_target.columns.tolist()
        col_code = [c for c in cols if '代號' in str(c) or '代碼' in str(c)][0]
        col_name = [c for c in cols if '名稱' in str(c)][0]
        col_weight = [c for c in cols if '權重' in str(c) or '比例' in str(c)][0]
        
        df_final = df_target[[col_code, col_name, col_weight]].copy()
        df_final.columns = ['代號', '名稱', '權重']
        
        # 清理代號 (確保純數字) 與 權重 (移除 %)
        df_final['代號'] = df_final['代號'].astype(str).str.extract('(\d+)')
        df_final['權重'] = pd.to_numeric(df_final['權重'].astype(str).str.replace('%', ''), errors='coerce')
        df_final = df_final.dropna(subset=['代號', '權重']).sort_values(by='權重', ascending=False)
        
        print(f"📊 情報擷取成功：共 {len(df_final)} 檔持股。")

        # 4. 歷史比對
        if os.path.exists(csv_file):
            df_old = pd.read_csv(csv_file)
            df_merge = pd.merge(df_final, df_old, on=['代號', '名稱'], how='outer', suffixes=('_新', '_舊')).fillna(0)
            df_merge['變化'] = df_merge['權重_新'] - df_merge['權重_舊']
            df_changed = df_merge[df_merge['變化'].abs() > 0.01].sort_values(by='變化', ascending=False)
            
            print("\n" + "="*30 + "\n🕵️‍♂️ 經理人【籌碼動向快報】\n" + "="*30)
            if df_changed.empty:
                print("▶️ 今日持倉比例極度穩定。")
            else:
                for _, row in df_changed.iterrows():
                    icon = "🟢 加碼" if row['變化'] > 0 else "🔴 減碼"
                    if row['權重_舊'] == 0: icon = "🆕 新進"
                    elif row['權重_新'] == 0: icon = "🚫 出清"
                    print(f"{icon} {row['名稱']}({row['代號']}): {row['變化']:+.2f}% (現: {row['權重_新']}%)")
            print("="*30)

        # 5. 存檔
        df_final.to_csv(csv_file, index=False, encoding='utf-8-sig')
        print(f"💾 歷史檔案已更新：{csv_file}")

    except Exception as e:
        print(f"❌ 偵察任務崩潰：{str(e)}")

if __name__ == "__main__":
    main()
