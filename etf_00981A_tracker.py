import os
import requests
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup

def main():
    # 🎯 V3 戰略目標：直攻統一投信 PCF 官方網頁
    PCF_URL = "https://www.ezmoney.com.tw/ETF/Transaction/PCFDetail?fundcode=49YTW" # 00981A 的底層代碼通常為 49YTW
    csv_file = "00981A_holdings.csv"
    today_str = datetime.now().strftime('%Y-%m-%d')
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 啟動【直攻 PCF V3】00981A 偵察任務...")
    
    try:
        # 1. 偽裝成瀏覽器去抓取網頁
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        res = requests.get(PCF_URL, headers=headers, timeout=20)
        res.raise_for_status()
        res.encoding = 'utf-8'
        
        # 2. 解析 HTML 表格 (找出包含成分股的 table)
        dfs = pd.read_html(res.text)
        
        # 尋找有「股票代號」的表格
        target_df = None
        for df in dfs:
            if '股票代號' in df.columns or '證券代碼' in df.columns or '代碼' in df.columns:
                target_df = df
                break
                
        if target_df is None:
            raise ValueError("❌ 在網頁中找不到成分股表格！")

        print(f"✅ PCF 網頁連線成功，接收到 {len(target_df)} 筆原始數據。")

        # 3. 清理數據與對齊欄位
        # 假設官網表格欄位包含：代碼、名稱、股數(或千股)、權重
        # 為了容錯，我們模糊匹配欄位名稱
        code_col = [c for c in target_df.columns if '代' in c][0]
        name_col = [c for c in target_df.columns if '名' in c][0]
        shares_col = [c for c in target_df.columns if '股' in c or '數' in c][0]
        weight_col = [c for c in target_df.columns if '權重' in c or '比' in c][0]

        df_today = pd.DataFrame()
        df_today['日期'] = [today_str] * len(target_df)
        df_today['代號'] = target_df[code_col].astype(str).str.strip()
        df_today['名稱'] = target_df[name_col].astype(str).str.strip()
        # 拔除數字中的逗號與 % 號，轉為浮點數
        df_today['股數'] = pd.to_numeric(target_df[shares_col].astype(str).str.replace(',', ''), errors='coerce')
        df_today['權重'] = pd.to_numeric(target_df[weight_col].astype(str).str.replace('%', ''), errors='coerce')
        
        # 過濾掉不完整的列（例如最後的加總列）
        df_today = df_today.dropna(subset=['代號', '權重'])
        
        print(f"📊 數據精煉完成，成功抓取『股數』欄位。今日有效持股共 {len(df_today)} 檔。")

        # 4. 讀取歷史檔案並進行疊加
        if os.path.exists(csv_file):
            df_history = pd.read_csv(csv_file, dtype={'代號': str})
            
            # 【無縫升級防呆】如果舊的 CSV 沒有「股數」欄位，幫它補上空值
            if '股數' not in df_history.columns:
                 df_history['股數'] = 0.0
                 
            # 刪除今日舊資料防重複
            df_history = df_history[df_history['日期'] != today_str]
            df_final = pd.concat([df_history, df_today], ignore_index=True)
        else:
            print("\n⚠️ 這是第一次執行，直接建立全新資料庫。")
            df_final = df_today

        # 5. 寫回 CSV
        df_final = df_final[['日期', '代號', '名稱', '權重', '股數']]
        df_final.to_csv(csv_file, index=False, encoding='utf-8-sig')
        print(f"\n💾 任務成功！包含【精確股數】的數據已寫入：{csv_file}")

    except Exception as e:
        print(f"\n❌ 衛星偵察發生故障：{str(e)}")

if __name__ == "__main__":
    main()
