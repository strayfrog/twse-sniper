import os
import time
import pandas as pd
from io import StringIO
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# 🎯 定義我們的高階雷達監控名單
ETF_TARGETS = ["00981A", "00991A", "00982A", "00980A"]

def scrape_etf_holdings(driver, etf_code, today_str):
    """專責深入敵營，撈取單一 ETF 持股並存成獨立 CSV"""
    
    pocket_url = f"https://www.pocket.tw/etf/tw/{etf_code}/fundholding/"
    csv_file = f"{etf_code}_holdings.csv"
    
    print(f"\n📍 駛入戰區 [{etf_code}]，強制等待 JavaScript 渲染...")
    driver.get(pocket_url)
    time.sleep(5)  # 強制等待 5 秒鐘
    
    html_content = driver.page_source
    dfs = pd.read_html(StringIO(html_content))
    
    # 暴力破解 HTML 表格
    target_df = None
    for df in dfs:
        cols_str = "".join([str(c) for c in df.columns])
        if '持有' in cols_str or '代號' in cols_str:
            target_df = df
            break
            
    if target_df is None:
        raise ValueError(f"❌ {etf_code} 找不到表格！網頁結構可能發生變動。")

    print(f"✅ [{etf_code}] 成功擊破空殼陷阱，接收到 {len(target_df)} 筆原始數據。")

    # 數據萃取與清理 
    code_col = [c for c in target_df.columns if '代碼' in str(c) or '代號' in str(c)][0]
    name_col = [c for c in target_df.columns if '名稱' in str(c)][0]
    shares_col = [c for c in target_df.columns if '持有' in str(c) or '數量' in str(c) or '張' in str(c) or '股' in str(c)][0]
    weight_col = [c for c in target_df.columns if '權重' in str(c) or '比例' in str(c)][0]

    df_today = pd.DataFrame()
    df_today['日期'] = [today_str] * len(target_df)
    df_today['代號'] = target_df[code_col].astype(str).str.strip()
    df_today['名稱'] = target_df[name_col].astype(str).str.strip()
    
    # 單位轉換：股數除以 1000 轉為張數
    raw_shares = pd.to_numeric(target_df[shares_col].astype(str).str.replace(',', ''), errors='coerce')
    df_today['張數'] = (raw_shares / 1000).fillna(0).astype(int)
    df_today['權重'] = pd.to_numeric(target_df[weight_col].astype(str).str.replace('%', ''), errors='coerce')
    
    # 啟動雜訊過濾防護罩
    df_today = df_today[~df_today['名稱'].str.contains('現金|元|價金|淨值|差異|合計', na=False)]
    df_today = df_today[~df_today['代號'].str.contains('NTD|合計', na=False)]
    df_today = df_today.dropna(subset=['代號', '權重'])
    df_today = df_today[df_today['張數'] > 0]

    print(f"📊 [{etf_code}] 有效持股共 {len(df_today)} 檔。準備進行歷史融合...")

    # 歷史檔案無縫疊加
    if os.path.exists(csv_file):
        df_history = pd.read_csv(csv_file, dtype={'代號': str})
        
        # 兼容舊版股數欄位自動升級
        if '股數' in df_history.columns:
            df_history['張數'] = (pd.to_numeric(df_history['股數'], errors='coerce') / 1000).fillna(0).astype(int)
            df_history = df_history.drop(columns=['股數'])
        elif '張數' not in df_history.columns:
             df_history['張數'] = 0
             
        df_history = df_history[df_history['日期'] != today_str]
        df_final = pd.concat([df_history, df_today], ignore_index=True)
    else:
        df_final = df_today

    # 寫回 CSV
    df_final = df_final[['日期', '代號', '名稱', '權重', '張數']]
    df_final.to_csv(csv_file, index=False, encoding='utf-8-sig')
    print(f"💾 [{etf_code}] 專屬純淨數據已寫入：{csv_file}")
    
    return csv_file # 回傳檔名，方便接續推送到 Google Drive

def push_to_google_drive(csv_filename):
    """
    這是一個對接接口。請在這裡放入總長原本寫好的 Google Drive 上傳邏輯。
    """
    print(f"🚀 啟動獨立空投：正在將 {csv_filename} 推送至 Google Drive 雲端總部...")
    # TODO: 貼上您原本使用的 PyDrive / Google API / gdrive CLI 的上傳代碼
    # 例如：
    # file = drive.CreateFile({'title': csv_filename, 'parents': [{'id': '您的雲端資料夾ID'}]})
    # file.SetContentFile(csv_filename)
    # file.Upload()
    print(f"✅ {csv_filename} 空投完成！\n" + "-"*40)


def main():
    today_str = datetime.now().strftime('%Y-%m-%d')
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 啟動【無頭裝甲車 V5.0 多管火箭版】偵察任務...")

    # 1. 統一啟動隱形裝甲車引擎 (只開一次瀏覽器，極大節省效能)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    print("啟動 Chrome 引擎...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # 2. 依序執行各個 ETF 戰區的掃描任務
        for etf in ETF_TARGETS:
            try:
                # 執行偵察，回傳獨立的 CSV 檔名 (如 00981A_holdings.csv)
                saved_csv = scrape_etf_holdings(driver, etf, today_str)
                
                # 3. 執行獨立推送：剛存好這個 ETF 的檔案，馬上推上雲端
                push_to_google_drive(saved_csv)
                
            except Exception as e:
                # 如果某一檔 ETF 出錯 (例如網頁剛好卡住)，攔截錯誤，不要讓整個程式崩潰，繼續掃描下一檔
                print(f"❌ 警告：[{etf}] 偵察發生故障：{str(e)}。跳過此檔，繼續執行下一個任務。")
                print("-" * 40)
                
    finally:
        # 4. 任務結束，裝甲車統一熄火
        driver.quit()
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🏁 所有 ETF 雷達掃描完畢，裝甲車已熄火收操！")

if __name__ == "__main__":
    main()
