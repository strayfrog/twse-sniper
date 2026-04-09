import os
import time
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def main():
    # 🎯 V4 終極裝甲版：派出 Headless Chrome 直攻口袋證券
    POCKET_URL = "https://www.pocket.tw/etf/tw/00981A/fundholding/"
    csv_file = "00981A_holdings.csv"
    today_str = datetime.now().strftime('%Y-%m-%d')
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 啟動【無頭裝甲車 V4】偵察任務...")

    try:
        # 1. 啟動隱形裝甲車 (Headless Chrome)
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # 不開啟實體視窗，在背景默默執行
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        print("啟動 Chrome 引擎...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # 2. 駛入目標戰區，強制等待渲染
        print("駛入口袋證券，埋伏等待 JavaScript 吐出持股張數...")
        driver.get(POCKET_URL)
        time.sleep(5)  # 關鍵破防點：強制等待 5 秒鐘！
        
        # 3. 獲取渲染後的「完整肉體」HTML
        html_content = driver.page_source
        driver.quit()
        
        # 4. 暴力破解 HTML 表格
        dfs = pd.read_html(html_content)
        
        # 尋找包含「數量」或「代碼」的目標表格
        target_df = None
        for df in dfs:
            cols_str = "".join([str(c) for c in df.columns])
            if '數量' in cols_str or '代碼' in cols_str or '代號' in cols_str:
                target_df = df
                break
                
        if target_df is None:
            raise ValueError("❌ 找不到表格！網頁結構可能發生變動。")

        print(f"✅ 成功擊破空殼陷阱，接收到 {len(target_df)} 筆真實數據。")

        # 5. 數據萃取與清理 (抓取代碼、名稱、數量、權重)
        code_col = [c for c in target_df.columns if '代碼' in str(c) or '代號' in str(c)][0]
        name_col = [c for c in target_df.columns if '名稱' in str(c)][0]
        shares_col = [c for c in target_df.columns if '數量' in str(c) or '張' in str(c) or '股' in str(c)][0]
        weight_col = [c for c in target_df.columns if '權重' in str(c) or '比例' in str(c)][0]

        df_today = pd.DataFrame()
        df_today['日期'] = [today_str] * len(target_df)
        df_today['代號'] = target_df[code_col].astype(str).str.strip()
        df_today['名稱'] = target_df[name_col].astype(str).str.strip()
        df_today['股數(張)'] = pd.to_numeric(target_df[shares_col].astype(str).str.replace(',', ''), errors='coerce')
        df_today['權重'] = pd.to_numeric(target_df[weight_col].astype(str).str.replace('%', ''), errors='coerce')
        
        df_today = df_today.dropna(subset=['代號', '權重'])
        print(f"📊 成功過濾！今日有效持股共 {len(df_today)} 檔。")

        # 6. 歷史檔案無縫疊加
        if os.path.exists(csv_file):
            df_history = pd.read_csv(csv_file, dtype={'代號': str})
            if '股數(張)' not in df_history.columns:
                 df_history['股數(張)'] = 0.0
            df_history = df_history[df_history['日期'] != today_str]
            df_final = pd.concat([df_history, df_today], ignore_index=True)
        else:
            df_final = df_today

        # 7. 寫回 CSV
        df_final = df_final[['日期', '代號', '名稱', '權重', '股數(張)']]
        df_final.to_csv(csv_file, index=False, encoding='utf-8-sig')
        print(f"\n💾 終極破防成功！包含【真實張數】的數據已寫入：{csv_file}")

    except Exception as e:
        print(f"\n❌ 裝甲車偵察發生故障：{str(e)}")

if __name__ == "__main__":
    main()
