import pandas as pd
import requests
import os
from datetime import datetime

def main():
    # 嘗試兩組可能的 API 網址 (統一投信常見的命名規則)
    api_url = "https://www.ezmoney.com.tw/ETF/Fund/HoldingJSON/?fundCode=49YTW"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Referer": "https://www.ezmoney.com.tw/ETF/Fund/Info?fundCode=49YTW",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive"
    }
    
    csv_file = "00981A_holdings.csv"
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 啟動 00981A 深度 API 偵察...")
    
    try:
        # 1. 執行請求
        res = requests.get(api_url, headers=headers, timeout=20)
        
        # 2. 戰略偵察：如果不是 JSON，先看它回傳了什麼
        print(f"📡 伺服器回應狀態碼: {res.status_code}")
        
        # 檢查是否為 JSON 格式
        try:
            data = res.json()
            print("✅ 成功解鎖 JSON 數據庫！")
        except:
            print("❌ 回傳並非 JSON 格式！對方可能丟了一個錯誤網頁過來。")
            print("-" * 50)
            print(f"對方回傳內容片段 (前500字)：\n{res.text[:500]}")
            print("-" * 50)
            return

        # 3. 數據轉換與清洗
        if not data:
            print("⚠️ 數據內容為空。")
            return

        df_new = pd.DataFrame(data)
        
        # 欄位對應 (統一 API 慣用欄位)
        if 'AccountName' in df_new.columns:
            df_new = df_new[['AccountCode', 'AccountName', 'Percentage']]
            df_new.columns = ['代號', '名稱', '權重']
        else:
            print(f"⚠️ 欄位名稱不符預期，現有欄位: {df_new.columns.tolist()}")
            return
            
        df_new['權重'] = pd.to_numeric(df_new['權重'], errors='coerce')
        print(f"📊 成功擷取 {len(df_new)} 筆持股資訊。")

        # 4. 籌碼變化比對
        if os.path.exists(csv_file):
            try:
                df_old = pd.read_csv(csv_file)
                df_merge = pd.merge(df_new, df_old, on=['代號', '名稱'], how='outer', suffixes=('_新', '_舊')).fillna(0)
                df_merge['變化'] = df_merge['權重_新'] - df_merge['權重_舊']
                df_changed = df_merge[df_merge['變化'].abs() > 0.05].sort_values(by='變化', ascending=False)
                
                print("\n--- 經理人陳釧瑤 籌碼變動偵報 ---")
                if df_changed.empty:
                    print("▶️ 今日無顯著變動，持倉平穩。")
                else:
                    for _, row in df_changed.iterrows():
                        icon = "🟢 加碼" if row['變化'] > 0 else "🔴 減碼"
                        print(f"{icon} {row['名稱']}: {row['變化']:+.2f}% (現: {row['權重_新']}%)")
            except Exception as e:
                print(f"⚠️ 比對引擎異常: {e}")
        
        # 5. 存檔入庫
        df_new.to_csv(csv_file, index=False, encoding='utf-8-sig')
        print(f"\n✅ 任務成功！歷史資料庫已更新至 {csv_file}")
        
    except Exception as e:
        print(f"\n❌ 偵察任務徹底崩潰：{str(e)}")

if __name__ == "__main__":
    main()
