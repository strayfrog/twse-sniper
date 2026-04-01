import pandas as pd
import requests
import os
from datetime import datetime

def main():
    # 🎯 證交所官方 PCF 數據接口 (JSON 格式)
    # 直接跟證交所要 00981A 的申購買回清單數據
    api_url = "https://www.twse.com.tw/exchangeReport/BW01_ETFP_PCF?response=json&etf_id=00981A"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    }
    
    csv_file = "00981A_holdings.csv"
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 啟動【證交所官方接口】偵察任務...")
    
    try:
        # 1. 取得 JSON 數據
        res = requests.get(api_url, headers=headers, timeout=20)
        res.raise_for_status()
        data_json = res.json()
        
        # 2. 判斷數據是否存在
        if "data" not in data_json or not data_json["data"]:
            print("⚠️ 證交所目前尚未提供今日數據 (通常 17:30 後更新)，請稍後再試。")
            return

        # 3. 轉換為 DataFrame
        # 證交所回傳的 data 是一個列表，每一行代表一檔股票
        # 根據證交所定義：[股票代碼, 股票名稱, ..., 權重] 
        # 我們需要抓取它的欄位索引
        raw_data = data_json["data"]
        fields = data_json["fields"]
        
        # 尋找關鍵欄位的索引位置
        idx_code = fields.index("股票代碼")
        idx_name = fields.index("股票名稱")
        idx_weight = fields.index("權重(%)")
        
        # 整理成我們需要的格式
        extracted_data = []
        for item in raw_data:
            extracted_data.append({
                "代號": item[idx_code],
                "名稱": item[idx_name],
                "權重": float(item[idx_weight])
            })
        
        df_new = pd.DataFrame(extracted_data).sort_values(by="權重", ascending=False)
        print(f"✅ 成功連線證交所！擷取到 {len(df_new)} 筆官方持股數據。")

        # 4. 歷史比對
        if os.path.exists(csv_file):
            try:
                df_old = pd.read_csv(csv_file)
                df_old['權重'] = df_old['權重'].astype(float)
                
                df_merge = pd.merge(df_new, df_old, on=['代號', '名稱'], how='outer', suffixes=('_新', '_舊')).fillna(0)
                df_merge['變化'] = df_merge['權重_新'] - df_merge['權重_舊']
                df_changed = df_merge[df_merge['變化'].abs() > 0.01].sort_values(by='變化', ascending=False)
                
                print("\n--- 經理人陳釧瑤 籌碼變動追蹤報告 ---")
                if df_changed.empty:
                    print("▶️ 今日持倉無顯著變動。")
                else:
                    for _, row in df_changed.iterrows():
                        icon = "🟢 加碼" if row['變化'] > 0 else "🔴 減碼"
                        print(f"{icon} {row['名稱']}({row['代號']}): {row['變化']:+.2f}% (現: {row['權重_新']}%)")
            except Exception as e:
                print(f"⚠️ 比對分析失敗: {e}")
        
        # 5. 存檔
        df_new.to_csv(csv_file, index=False, encoding='utf-8-sig')
        print(f"💾 官方數據已存入：{csv_file}")
        
    except Exception as e:
        print(f"❌ 證交所 API 偵察失敗：{str(e)}")

if __name__ == "__main__":
    main()
