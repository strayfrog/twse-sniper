import os
import requests
import pandas as pd
from datetime import datetime

def main():
    # 🎯 V3.1 戰略目標：直攻口袋證券 00981A 持股網頁
    POCKET_URL = "https://www.pocket.tw/etf/tw/00981A/fundholding/"
    csv_file = "00981A_holdings.csv"
    today_str = datetime.now().strftime('%Y-%m-%d')
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 啟動【口袋證券 V3.1】偵察任務...")
    
    try:
        # 1. 強力偽裝，突破基礎防爬蟲機制
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7'
        }
        res = requests.get(POCKET_URL, headers=headers, timeout=20)
        res.raise_for_status()
        res.encoding = 'utf-8'
        
        # 2. 暴力破解 HTML 表格
        dfs = pd.read_html(res.text)
        
        # 尋找包含「數量」或「代碼」的目標表格
        target_df = None
        for df in dfs:
            # 將欄位名稱轉為字串並檢查
            cols_str = "".join([str(c) for c in df.columns])
            if '數量' in cols_str or '代碼' in cols_str or '代號' in cols_str:
                target_df = df
                break
                
        if target_df is None:
            raise ValueError("❌ 找不到包含成分股的表格！(口袋證券可能啟用了動態 JS 渲染)")

        print(f"✅ 目標網頁連線成功，接收到 {len(target_df)} 筆原始數據。")

        # 3. 數據萃取與清理 (動態匹配您截圖中的欄位)
        code_col = [c for c in target_df.columns if '代碼' in str(c) or '代號' in str(c)][0]
        name_col = [c for c in target_df.columns if '名稱' in str(c)][0]
        shares_col = [c for c in target_df.columns if '數量' in str(c) or '張' in str(c) or '股' in str(c)][0]
        weight_col = [c for c in target_df.columns if '權重' in str(c) or '比例' in str(c)][0]

        df_today = pd.DataFrame()
        df_today['日期'] = [today_str] * len(target_df)
        df_today['代號'] = target_df[code_col].astype(str).str.strip()
        df_today['名稱'] = target_df[name_col].astype(str).str.strip()
        
        # 清除千分位逗號與 % 號，並轉為純數字
        df_today['股數(張)'] = pd.to_numeric(target_df[shares_col].astype(str).str.replace(',', ''), errors='coerce')
        df_today['權重'] = pd.to_numeric(target_df[weight_col].astype(str).str.replace('%', ''), errors='coerce')
        
        # 過濾無效列
        df_today = df_today.dropna(subset=['代號', '權重'])
        
        print(f"📊 成功抓取『持有數量』。今日有效持股共 {len(df_today)} 檔。")

        # 4. 歷史檔案無縫疊加作業
        if os.path.exists(csv_file):
            df_history = pd.read_csv(csv_file, dtype={'代號': str})
            
            # 【無縫防呆】：如果您舊的 CSV 沒有這個新欄位，自動補上 0 避免程式崩潰
            if '股數(張)' not in df_history.columns:
                 df_history['股數(張)'] = 0.0
                 
            df_history = df_history[df_history['日期'] != today_str]
            df_final = pd.concat([df_history, df_today], ignore_index=True)
        else:
            df_final = df_today

        # 5. 寫回 CSV (將「股數」正式編入部隊)
        df_final = df_final[['日期', '代號', '名稱', '權重', '股數(張)']]
        df_final.to_csv(csv_file, index=False, encoding='utf-8-sig')
        print(f"\n💾 任務成功！包含【張數】的終極戰略數據已寫入：{csv_file}")

    except Exception as e:
        print(f"\n❌ 衛星偵察發生故障：{str(e)}")

if __name__ == "__main__":
    main()
