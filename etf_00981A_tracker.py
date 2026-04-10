import os
import time
import pandas as pd
import traceback
from io import StringIO
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

ETF_TARGETS = ["00981A", "00991A", "00982A", "00980A"]

def scrape_etf_holdings(driver, etf_code, today_str):
    pocket_url = f"https://www.pocket.tw/etf/tw/{etf_code}/fundholding/"
    csv_file = f"{etf_code}_holdings.csv"
    
    print(f"\n📍 駛入戰區 [{etf_code}]，網址: {pocket_url}")
    driver.get(pocket_url)
    time.sleep(8)  # 延長等待時間，怕 GitHub 主機跑太慢
    
    html_content = driver.page_source
    
    try:
        dfs = pd.read_html(StringIO(html_content))
        
        target_df = None
        for df in dfs:
            cols_str = "".join([str(c) for c in df.columns])
            if '持有' in cols_str or '代號' in cols_str:
                target_df = df
                break
                
        if target_df is None:
            raise ValueError(f"找不到表格！")

        print(f"✅ [{etf_code}] 成功抓到表格！")
        
        code_col = [c for c in target_df.columns if '代碼' in str(c) or '代號' in str(c)][0]
        name_col = [c for c in target_df.columns if '名稱' in str(c)][0]
        shares_col = [c for c in target_df.columns if '持有' in str(c) or '數量' in str(c) or '張' in str(c) or '股' in str(c)][0]
        weight_col = [c for c in target_df.columns if '權重' in str(c) or '比例' in str(c)][0]

        df_today = pd.DataFrame()
        df_today['日期'] = [today_str] * len(target_df)
        df_today['代號'] = target_df[code_col].astype(str).str.strip()
        df_today['名稱'] = target_df[name_col].astype(str).str.strip()
        
        raw_shares = pd.to_numeric(target_df[shares_col].astype(str).str.replace(',', ''), errors='coerce')
        df_today['張數'] = (raw_shares / 1000).fillna(0).astype(int)
        df_today['權重'] = pd.to_numeric(target_df[weight_col].astype(str).str.replace('%', ''), errors='coerce')
        
        df_today = df_today[~df_today['名稱'].str.contains('現金|元|價金|淨值|差異|合計', na=False)]
        df_today = df_today[~df_today['代號'].str.contains('NTD|合計', na=False)]
        df_today = df_today.dropna(subset=['代號', '權重'])
        df_today = df_today[df_today['張數'] > 0]

        if os.path.exists(csv_file):
            df_history = pd.read_csv(csv_file, dtype={'代號': str})
            if '股數' in df_history.columns:
                df_history['張數'] = (pd.to_numeric(df_history['股數'], errors='coerce') / 1000).fillna(0).astype(int)
                df_history = df_history.drop(columns=['股數'])
            elif '張數' not in df_history.columns:
                 df_history['張數'] = 0
            df_history = df_history[df_history['日期'] != today_str]
            df_final = pd.concat([df_history, df_today], ignore_index=True)
        else:
            df_final = df_today

        df_final = df_final[['日期', '代號', '名稱', '權重', '張數']]
        df_final.to_csv(csv_file, index=False, encoding='utf-8-sig')
        print(f"💾 [{etf_code}] 寫入成功：{csv_file}")
        
    except Exception as e:
        # 🚨 黑盒子啟動：如果出錯，拍下截圖並儲存 HTML 原始碼！
        print(f"\n❌ [{etf_code}] 發生致命錯誤：{e}")
        print("🔍 正在列印錯誤堆疊：")
        traceback.print_exc()
        
        screenshot_path = f"error_{etf_code}.png"
        html_path = f"error_{etf_code}.html"
        driver.save_screenshot(screenshot_path)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        print(f"📸 已拍下案發現場截圖：{screenshot_path}，以及 HTML 原始碼：{html_path}")
        print("請將 YAML 檔的 `git add` 改為 `git add *`，把這些證據一起帶回來！\n")

def main():
    today_str = datetime.now().strftime('%Y-%m-%d')
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 啟動【黑盒子除錯版】...")

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("window-size=1920x1080") # 強制設定視窗大小，避免排版跑掉
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        for etf in ETF_TARGETS:
            scrape_etf_holdings(driver, etf, today_str)
    finally:
        driver.quit()
        print("\n🏁 掃描完畢！")

if __name__ == "__main__":
    main()
