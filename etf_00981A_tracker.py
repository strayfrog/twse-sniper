import os
import time
import pandas as pd
from io import StringIO
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def main():
    # 🎯 V4.2 終極裝甲版：直攻口袋證券，並配備「雜訊粉碎防護罩」
    POCKET_URL = "https://www.pocket.tw/etf/tw/00981A/fundholding/"
    csv_file = "00981A_holdings.csv"
    today_str = datetime.now().strftime('%Y-%m-%d')
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 啟動【無頭裝甲車 V4.2】偵察任務...")

    try:
        # 1. 啟動隱形裝甲車
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        print("啟動 Chrome 引擎...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # 2. 駛入目標戰區，強制等待渲染
        print("駛入口袋證券，埋伏等待 JavaScript 吐出持股張數...")
        driver.get(POCKET_URL)
        time.sleep(5)  # 強制等待 5 秒鐘
        
        # 3. 獲取渲染後的 HTML
        html_content = driver.page_source
        driver.quit()
        
        # 4. 暴力破解 HTML 表格 (使用 StringIO 修復 Future Warning)
        dfs = pd.read_html(StringIO(html_content))
        
        # 尋找目標表格
        target_df = None
        for df in dfs:
            cols_str = "".join([str(c) for c in df.columns])
            if '持有' in cols_str or '代號' in cols_str:
                target_df = df
                break
                
        if target_df is None:
            raise ValueError("❌ 找不到表格！網頁結構可能發生變動。")

        print(f"✅ 成功擊破空殼陷阱，接收到 {len(target_df)} 筆原始數據。")
        print(f"🔍 戰術雷達掃描到的欄位名稱為: {list(target_df.columns)}") # 除錯雷達

        # 5. 數據萃取與清理 (加入 '持有' 關鍵字防呆)
        try:
            code_col = [c for c in target_df.columns if '代碼' in str(c) or '代號' in str(c)][0]
            name_col = [c for c in target_df.columns if '名稱' in str(c)][0]
            # 新增鎖定 '持有'
            shares_col = [c for c in target_df.columns if '持有' in str(c) or '數量' in str(c) or '張' in str(c) or '股' in str(c)][0]
            weight_col = [c for c in target_df.columns if '權重' in str(c) or '比例' in str(c)][0]
        except IndexError as e:
            raise ValueError(f"❌ 欄位匹配失敗！請回報上述『雷達掃描到的欄位名稱』給情報官！")

        df_today = pd.DataFrame()
        df_today['日期'] = [today_str] * len(target_df)
        df_today['代號'] = target_df[code_col].astype(str).str.strip()
        df_today['名稱'] = target_df[name_col].astype(str).str.strip()
        df_today['股數'] = pd.to_numeric(target_df[shares_col].astype(str).str.replace(',', ''), errors='coerce')
        df_today['權重'] = pd.to_numeric(target_df[weight_col].astype(str).str.replace('%', ''), errors='coerce')
        
        # ==========================================
        # 🛡️ 啟動雜訊過濾防護罩 (V4.2 新增核心)
        # ==========================================
        # 1. 踢除名稱裡包含「現金」、「元」、「價金」、「淨值」、「差異」的列
        df_today = df_today[~df_today['名稱'].str.contains('現金|元|價金|淨值|差異|合計', na=False)]
        
        # 2. 踢除代號欄位出現奇怪字眼的列 (例如 NTD)
        df_today = df_today[~df_today['代號'].str.contains('NTD|合計', na=False)]
        
        # 3. 清除轉換失敗的空值，確保代號、權重、股數都必須存在
        df_today = df_today.dropna(subset=['代號', '權重', '股數'])
        # ==========================================

        print(f"📊 成功過濾雜訊！今日有效「純股票」持股共 {len(df_today)} 檔。")

        # 6. 歷史檔案無縫疊加
        if os.path.exists(csv_file):
            df_history = pd.read_csv(csv_file, dtype={'代號': str})
            if '股數' not in df_history.columns:
                 df_history['股數'] = 0.0
            df_history = df_history[df_history['日期'] != today_str]
            df_final = pd.concat([df_history, df_today], ignore_index=True)
        else:
            df_final = df_today

        # 7. 寫回 CSV
        df_final = df_final[['日期', '代號', '名稱', '權重', '股數']]
        df_final.to_csv(csv_file, index=False, encoding='utf-8-sig')
        print(f"\n💾 終極破防成功！純淨數據已寫入：{csv_file}")

    except Exception as e:
        print(f"\n❌ 裝甲車偵察發生故障：{str(e)}")

if __name__ == "__main__":
    main()
