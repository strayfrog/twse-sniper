import pandas as pd
import requests
import os
from datetime import datetime

def main():
    # 🎯 這是直接捅進後台資料庫的 API 網址
    # 它會直接返回 00981A 的最新持股數據，繞過所有網頁渲染
    api_url = "https://www.ezmoney.com.tw/ETF/Fund/HoldingJSON/?fundCode=49YTW"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Referer": "https://www.ezmoney.com.tw/ETF/Fund/Info?fundCode=49YTW"
    }
    
    csv_file = "00981A_holdings.csv"
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 啟動 00981A API 偵察任務...")
    
    try:
        # 1. 向 API 請求數據
        res = requests.get(api_url, headers=headers, timeout=20)
        res.raise_for_status()
        
        # 2. 解析 JSON 數據
        # 統一的 API 會返回一個列表，每個物件包含：AccountCode(代號), AccountName(名稱), Percentage(權重)
        data = res.json()
        
        if not data:
            print("⚠️ API 回傳數據為空，可能尚未更新或代號錯誤。")
            return

        # 3. 轉換為 DataFrame
        # 根據觀察，API 欄位為: 'AccountCode', 'AccountName', 'Percentage'
        df_new = pd.DataFrame(data)
        
        # 只保留我們需要的欄位並重新命名
        df_new = df_new[['AccountCode', 'AccountName', 'Percentage']]
        df_new.columns = ['代號', '名稱', '權重']
        
        # 確保權重是數字
        df_new['權重'] = pd.to_numeric(df_new['權重'], errors='coerce')
        print(f"成功從 API 取得 {len(df_new)} 筆持股清單！")

        # 4. 比對舊資料
        if os.path.exists(csv_file):
            try:
                df_old = pd.read_csv(csv_file)
                df_merge = pd.merge(df_new, df_old, on=['代號', '名稱'], how='outer', suffixes=('_新', '_舊')).fillna(0)
                df_merge['變化'] = df_merge['權重_新'] - df_merge['權重_舊']
                
                df_changed = df_merge[df_merge['變化'].abs() > 0.05].sort_values(by='變化', ascending=False)
                
                print("\n--- 經理人籌碼變化報告 ---")
                if df_changed.empty:
                    print("▶️ 今日無顯著變動，經理人穩定持倉。")
                else:
                    for _, row in df_changed.iterrows():
                        icon = "🟢 加碼" if row['變化'] > 0 else "🔴 減碼"
                        print(f"{icon} {row['名稱']}: {row['變化']:+.2f}% (現: {row['權重_新']}%)")
            except Exception as e:
                print(f"⚠️ 比對過程中發生問題: {e}")
        
        # 5. 存檔入庫
        df_new.to_csv(csv_file, index=False, encoding='utf-8-sig')
        print(f"\n✅ 任務成功！API 數據已同步至 {csv_file}")
        
    except Exception as e:
        print(f"\n❌ API 偵察崩潰！錯誤診斷: {str(e)}")

if __name__ == "__main__":
    main()
