import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# 每 30 秒自動刷新數據
st_autorefresh(interval=30000, key="datarefresh")

st.set_page_config(page_title="全球股市 Dashboard", layout="wide")
st.title("🌐 全球主要股市與龍頭股實時監控")

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
        "Bitcoin (BTC)": "BTC-USD"
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
            
            # 1. 顯示頂部數據卡片
            col.metric(
                label=name,
                value=f"{price:,.2f}",
                delta=f"{change:+.2f} ({pct_change:+.2f}%)"
            )
            
            # 2. 抓取當日 15 分鐘級別走勢數據
            hist = stock.history(period="1d", interval="15m")
            if not hist.empty:
                # 正數顯示綠色，負數顯示紅色
                line_color = "#00c805" if change >= 0 else "#ff5000"
                
                # 建立精簡 Sparkline 走勢圖
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=hist.index,
                    y=hist["Close"],
                    mode="lines",
                    line=dict(color=line_color, width=2),
                    hoverinfo="none"
                ))
                
                # 隱藏 X/Y 軸文字，自動放縮 Y 軸範圍
                fig.update_layout(
                    margin=dict(l=0, r=0, t=0, b=0),
                    height=50,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(visible=False),
                    yaxis=dict(visible=False, autorange=True),
                    showlegend=False
                )
                
                col.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        except Exception:
            col.error(f"{name} 載入失敗")
