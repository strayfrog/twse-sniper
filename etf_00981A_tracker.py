import pandas as pd
import requests
import os
from datetime import datetime
from io import StringIO

def main():
    # 🎯 戰略目標：鉅亨網 (Anue) 的 00981A 持股頁面
    # 這個網頁專門整理各家 ETF 的最新成分股，非常穩定
    target_url = "https://invest.cnyes.com/etf/tw/00981A/holdings"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Referer": "https://invest.cnyes.com/"
    }
    
    csv_file = "00981A_holdings.csv"
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 啟動【鉅亨網】00981A 偵察任務...")
    
    try:
        # 1. 取得網頁 HTML
        res = requests.get(target_url, headers=headers, timeout=20)
        res.raise_for_status()
        
        # 2. 使用 pandas 直接解析 HTML 中的表格
        # 鉅亨網的持股表格通常含有「持股名稱」或「權重」等字眼
        tables = pd.read_html(StringIO(res.text))
        
        # 尋找含有持股特徵的表格
        df_target = None
        for t in tables:
            # 鉅亨網的欄位通常是：持股名稱, 股票代號, 權重(%) ...
            cols_str = "".join(t.columns.astype(str))
            if "名稱" in cols_str and "權重" in cols_str:
                df_target = t
                break
        
        if df_target is None:
            print("❌ 錯誤：在鉅亨網頁面中找不到持股表格。")
            return

        # 3. 數據清理：統一欄位格式為 [代號, 名稱, 權重]
        # 鉅亨網欄位可能順序不同，我們用關鍵字精準抓取
        cols = df_target.columns.tolist()
        col_name = [c for c in cols if '名稱' in str(c)][0]
        col_code = [c for c in cols if '代號' in str(c) or '代碼' in str(c)][0]
        col_weight = [c for c in cols if '權重' in str(c)][0]
        
        df_final = df_target[[col_code, col_name, col_weight]].copy()
        df_final.columns = ['代號', '名稱', '權重']
        
        # 清理權重欄位 (移除 % 並轉為數字)
        df_final['權重'] = pd.to_numeric(df_final['權重'].astype(str).str.replace('%', ''), errors='coerce')
        df_final = df_final.sort_values(by='權重', ascending=False)
        
        print(f"✅ 成功從鉅亨網擷取到 {len(df_final)} 筆持股數據！")

        # 4. 歷史比對與籌碼變化報告
        if os.path.exists(csv_file):
            try:
                df_old = pd.read_csv(csv_file)
                df_merge = pd.merge(df_final, df_old, on=['代號', '名稱'], how='outer', suffixes=('_新', '_舊')).fillna(0)
                df_merge['變化'] = df_merge['權重_新'] - df_merge['權重_舊']
                
                # 過濾變化量大於 0.01% 的動作
                df_changed = df_merge[df_merge['變化'].abs() > 0.01].sort_values(by='變化', ascending=False)
                
                print("\n" + "="*30)
                print("🕵️‍♂️ 經理人陳釧瑤【籌碼動向報】")
                print("="*30)
                if df_changed.empty:
                    print("▶️ 今日持倉比例極度穩定，經理人無顯著動作。")
                else:
                    for _, row in df_changed.iterrows():
                        icon = "🟢 加碼" if row['變化'] > 0 else "🔴 減碼"
                        # 如果是新出現的股票
                        if row['權重_舊'] == 0:
                            icon = "🆕 新進"
                        # 如果是消失的股票
                        elif row['權重_新'] == 0:
                            icon = "🚫 出清"
                            
                        print(f"{icon} {row['名稱']}({row['代號']}): {row['變化']:+.2f}% (現: {row['權重_新']}%)")
                print("="*30)
            except Exception as e:
                print(f"⚠️ 比對分析發生錯誤: {e}")

        # 5. 存檔
        df_final.to_csv(csv_file, index=False, encoding='utf-8-sig')
        print(f"\n💾 數據已入庫：{csv_file}")

    except Exception as e:
        print(f"❌ 鉅亨網偵察失敗：{str(e)}")

if __name__ == "__main__":
    main()
