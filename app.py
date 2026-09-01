import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# 設定每 10 秒 (10000 毫秒) 自動重新載入頁面數據
st_autorefresh(interval=10000, key="datarefresh")

st.set_page_config(page_title="全球股市 Dashboard", layout="wide")
st.title("🌐 全球主要股市與龍頭股實時監控")

# 在這裡隨時新增、刪除或修改你的股票清單！
targets = {
    "主要股市指數": {
        "恒生指數 (HK)": "^HSI",
        "上證指數 (CN)": "000001.SS",
        "台灣加權 (TW)": "^TWII",
        "日經 225 (JP)": "^N225",
        "韓國 KOSPI (KR)": "^KS11",
        "美國 S&P 500 (US)": "^GSPC"
    },
    "市場市值龍頭": {
        "騰訊控股 (0700)": "0700.HK",
        "貴州茅台 (600519)": "600519.SS",
        "台積電 (2330)": "2330.TW",
        "豐田汽車 (7203)": "7203.T",
        "三星電子 (005930)": "005930.KS",
        "NVIDIA (NVDA)": "NVDA"
    },
    "⭐ 我的自選股": {
        "Tesla (TSLA)": "TSLA",
        "Apple (AAPL)": "AAPL",
        "美團 (3690)": "3690.HK",
        "匯豐控股 (0005)": "0005.HK",
        "Colgate-Palmolive (CL)": "CL"
    }
}

for category, items in targets.items():
    st.markdown(f"### 📌 {category}")
    cols = st.columns(len(items))
    for col, (name, ticker) in zip(cols, items.items()):
        try:
            stock = yf.Ticker(ticker)
            info = stock.fast_info
            
            price = info.last_price
            prev_close = info.previous_close
            change = price - prev_close
            pct_change = (change / prev_close) * 100
            
            col.metric(
                label=name,
                value=f"{price:,.2f}",
                delta=f"{change:+.2f} ({pct_change:+.2f}%)"
            )
        except Exception:
            col.error(f"{name} 載入失敗")
