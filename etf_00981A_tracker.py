import pandas as pd
import requests
import os
from datetime import datetime

# ==========================================
# 00981A 籌碼情報偵察兵 (獨立模組)
# ==========================================

# LINE Notify 設定 (從 GitHub Secrets 讀取)
LINE_TOKEN = os.environ.get("LINE_TOKEN")

def send_line_notify(msg):
    if not LINE_TOKEN:
        print("未設定 LINE_TOKEN，略過發送訊息。")
        return
    headers = {"Authorization": f"Bearer {LINE_TOKEN}"}
    data = {"message": msg}
    requests.post("https://notify-api.line.me/api/notify", headers=headers, data=data)

def main():
    url = "https://www.ezmoney.com.tw/ETF/Fund/Info?fundCode=49YTW"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    csv_file = "00981A_holdings.csv"
    
    report_str = "\n🕵️‍♂️ [情報部隊] 00981A 經理人底牌追蹤\n" + "="*25 + "\n"
    
    try:
        # 1. 抓取今日最新資料
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        tables = pd.read_html(res.text)
        
        # 抓取表格前三欄：代號、名稱、權重
        df_new = tables[0].iloc[:, [0, 1, 2]]
        df_new.columns = ['代號', '名稱', '權重']
        
        # 清除 % 符號並轉為數字
        df_new['權重'] = df_new['權重'].astype(str).str.replace('%', '', regex=False).astype(float)
        
        # 2. 比對昨日資料庫
        if os.path.exists(csv_file):
            df_old = pd.read_csv(csv_file)
            # 合併比對
            df_merge = pd.merge(df_new, df_old, on=['代號', '名稱'], how='outer', suffixes=('_新', '_舊')).fillna(0)
            df_merge['變化'] = df_merge['權重_新'] - df_merge['權重_舊']
            
            # 過濾微小誤差 (變化 > 0.05% 才視為經理人有主動動作)
            df_changed = df_merge[df_merge['變化'].abs() > 0.05].sort_values(by='變化', ascending=False)
            
            if df_changed.empty:
                report_str += "▶️ 今日前十大持股無顯著變動，經理人按兵不動。\n"
            else:
                for _, row in df_changed.iterrows():
                    icon = "🟢 加碼" if row['變化'] > 0 else "🔴 減碼"
                    report_str += f"{icon} {row['名稱']}: {row['變化']:+.2f}% (現: {row['權重_新']}%)\n"
        else:
            report_str += "⚠️ 偵察兵初次建檔完成，明日盤後將開始發送籌碼變化對比。\n"
            
        # 3. 覆蓋存檔，交由 GitHub Actions 上傳
        df_new.to_csv(csv_file, index=False, encoding='utf-8-sig')
        
    except Exception as e:
        report_str += f"❌ 偵察任務失敗：網頁結構可能已更改。\n錯誤訊息: {str(e)[:100]}\n"
        
    # 4. 發送情報至總長手機
    send_line_notify(report_str)
    print("偵察任務結束，情報已發送。")

if __name__ == "__main__":
    main()
