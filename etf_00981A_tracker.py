import pandas as pd
import requests
import os
from datetime import datetime
from io import StringIO
from bs4 import BeautifulSoup

def main():
    # 🎯 戰術目標：口袋證券 (Pocket) 00981A 持股頁面
    url = "https://www.pocket.tw/etf/tw/00981A/fundholding/"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive"
    }
    
    csv_file = "00981A_holdings.csv"
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 啟動【口袋證券】00981A 偵察任務...")
    
    try:
        # 1. 取得網頁原始碼
        res = requests.get(url, headers=headers, timeout=20)
        res.raise_for_status()
        
        # 2. 戰略偵察：這一步很重要，如果口袋證券是動態渲染，這裏會抓不到 table
        soup = BeautifulSoup(res.text, 'html.parser')
        tables = pd.read_html(StringIO(res.text))
        
        print(f"📡 網頁掃描完成，偵測到 {len(tables)} 個表格區域。")

        df_target = None
        # 3. 尋找持股表格 (口袋證券通常會有「代碼」與「比例」)
        for t in tables:
            cols_str = "".join(t.columns.astype(str))
            if "名稱" in cols_str or "權重" in cols_str or "比重" in cols_str:
                df_target = t
                break
        
        if df_target is None:
            print("❌ 偵察失敗：口袋證券的表格是動態生成的，一般爬蟲抓不到。")
            print("--- 偵錯資訊：抓到的網頁開頭如下 ---")
            print(res.text[:500]) # 讓我們看看它是不是噴了 Cloudflare 的阻擋頁面
            return

        # 4. 數據清理 (假設欄位為: 名稱, 代號, 權重...)
        # 根據口袋證券常見排版進行對應
        cols = df_target.columns.tolist()
        col_code = [c for c in cols if '代號' in str(c) or '代碼' in str(c)][0]
        col_name = [c for c in cols if '名稱' in str(c)][0]
        col_weight = [c for c in cols if '權重' in str(c) or '比重' in str(c) or '比例' in str(c)][0]
        
        df_final = df_target[[col_code, col_name, col_weight]].copy()
        df_final.columns = ['代號', '名稱', '權重']
        
        # 轉換數字
        df_final['權重'] = pd.to_numeric(df_final['權重'].astype(str).str.replace('%', ''), errors='coerce')
        df_final = df_final.dropna(subset=['代號', '權重']).sort_values(by='權重', ascending=False)
        
        print(f"🎯 成功！擷取到 {len(df_final)} 筆核心持股資料。")

        # 5. 籌碼比對 (比對歷史 CSV)
        if os.path.exists(csv_file):
            df_old = pd.read_csv(csv_file)
            df_merge = pd.merge(df_final, df_old, on=['代號', '名稱'], how='outer', suffixes=('_新', '_舊')).fillna(0)
            df_merge['變化'] = df_merge['權重_新'] - df_merge['權重_舊']
            
            df_changed = df_merge[df_merge['變化'].abs() > 0.01].sort_values(by='變化', ascending=False)
            
            print("\n" + "="*35 + "\n🕵️‍♂️ 經理人陳釧瑤【最新籌碼動向】\n" + "="*35)
            if df_changed.empty:
                print("▶️ 今日持倉極度穩定。")
            else:
                for _, row in df_changed.iterrows():
                    icon = "🟢 加碼" if row['變化'] > 0 else "🔴 減碼"
                    if row['權重_舊'] == 0: icon = "🆕 新進"
                    elif row['權重_新'] == 0: icon = "🚫 出清"
                    print(f"{icon} {row['名稱']}({row['代號']}): {row['變化']:+.2f}% (現: {row['權重_新']}%)")
            print("="*35)

        # 6. 存檔更新
        df_final.to_csv(csv_file, index=False, encoding='utf-8-sig')
        print(f"💾 歷史檔案已同步：{csv_file}")

    except Exception as e:
        print(f"❌ 口袋證券偵察崩潰：{str(e)}")

if __name__ == "__main__":
    main()
