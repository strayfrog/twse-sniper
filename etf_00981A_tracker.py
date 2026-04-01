import pandas as pd
import requests
import os
from datetime import datetime

# ==========================================
# 00981A 籌碼情報偵察兵 (強攻 HTML 解析版)
# ==========================================

def main():
    url = "https://www.ezmoney.com.tw/ETF/Fund/Info?fundCode=49YTW"
    
    # 強力偽裝標頭，避免被投信網站的防火牆 (WAF) 擋下
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive"
    }
    
    csv_file = "00981A_holdings.csv"
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 啟動 00981A 籌碼偵察任務...")
    
    try:
        # 1. 發送請求取得網頁 HTML
        print("正在突破敵方網頁防火牆...")
        res = requests.get(url, headers=headers, timeout=15)
        res.raise_for_status() # 如果被擋(403)或找不到網頁(404)，會在這裡報錯
        print("成功取得網頁原始碼！")

        # 2. 精準解析表格 (利用 match 參數尋找包含特定字眼的表格)
        # 統一網站上的表頭叫做「股票名稱」，我們就叫 pandas 去找這個詞
        tables = pd.read_html(res.text, match='股票名稱')
        
        if not tables:
             raise ValueError("在網頁中找不到含有 '股票名稱' 的表格，網頁排版可能已大改！")
             
        df_new = tables[0]
        print("成功定位持股表格！")
        
        # 3. 處理欄位與資料格式
        df_new = df_new.iloc[:, [0, 1, 2]] # 抓取代號、名稱、權重
        df_new.columns = ['代號', '名稱', '權重']
        
        # 清除 % 符號並轉為浮點數
        df_new['權重'] = df_new['權重'].astype(str).str.replace('%', '', regex=False).astype(float)
        
        # 4. 比對昨日資料庫 (若存在)
        if os.path.exists(csv_file):
            df_old = pd.read_csv(csv_file)
            df_merge = pd.merge(df_new, df_old, on=['代號', '名稱'], how='outer', suffixes=('_新', '_舊')).fillna(0)
            df_merge['變化'] = df_merge['權重_新'] - df_merge['權重_舊']
            
            df_changed = df_merge[df_merge['變化'].abs() > 0.05].sort_values(by='變化', ascending=False)
            
            print("\n--- 經理人籌碼變化 (權重變化 > 0.05%) ---")
            if df_changed.empty:
                print("▶️ 今日前十大持股無顯著變動。")
            else:
                for _, row in df_changed.iterrows():
                    icon = "🟢 加碼" if row['變化'] > 0 else "🔴 減碼"
                    print(f"{icon} {row['名稱']}: {row['變化']:+.2f}% (現: {row['權重_新']}%)")
        else:
            print("\n⚠️ 找不到舊檔案，今日將建立初始 CSV 資料庫。")
            
        # 5. 存檔
        df_new.to_csv(csv_file, index=False, encoding='utf-8-sig')
        print(f"\n✅ 任務成功！最新持股已更新至 {csv_file}")
        
    except Exception as e:
        print(f"\n❌ 偵察任務失敗！")
        print(f"錯誤診斷: {str(e)[:250]}")

if __name__ == "__main__":
    main()
