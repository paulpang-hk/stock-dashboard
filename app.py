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

def create_dynamic_sparkline(hist, prev_close):
    fig = go.Figure()
    if hist.empty:
        return fig
        
    x_vals = hist.index.tolist()
    y_vals = hist["Close"].tolist()
    ref_val = prev_close
    
    # 1. 加入昨收基準線 (灰色點線)
    fig.add_trace(go.Scatter(
        x=[x_vals[0], x_vals[-1]],
        y=[ref_val, ref_val],
        mode="lines",
        line=dict(color="rgba(150, 150, 150, 0.6)", width=1, dash="dot"),
        hoverinfo="none",
        showlegend=False
    ))
    
    # 2. 計算與昨收基準線的交點，確保顏色切換平滑
    new_x = []
    new_y = []
    for i in range(len(y_vals) - 1):
        x1, x2 = x_vals[i], x_vals[i+1]
        y1, y2 = y_vals[i], y_vals[i+1]
        new_x.append(x1)
        new_y.append(y1)
        
        if (y1 < ref_val and y2 > ref_val) or (y1 > ref_val and y2 < ref_val):
            t = (ref_val - y1) / (y2 - y1)
            x_cross = x1 + (x2 - x1) * t
            new_x.append(x_cross)
            new_y.append(ref_val)
            
    new_x.append(x_vals[-1])
    new_y.append(y_vals[-1])
    
    # 3. 分割為高於昨收 (綠色) 與低於昨收 (紅色) 的線段
    curr_x = [new_x[0]]
    curr_y = [new_y[0]]
    curr_above = new_y[0] >= ref_val
    
    for i in range(1, len(new_y)):
        val = new_y[i]
        is_above = val >= ref_val
        
        if val == ref_val:
            curr_x.append(new_x[i])
            curr_y.append(new_y[i])
        elif is_above == curr_above:
            curr_x.append(new_x[i])
            curr_y.append(new_y[i])
        else:
            color = "#00c805" if curr_above else "#ff5000"
            fig.add_trace(go.Scatter(
                x=curr_x, y=curr_y,
                mode="lines",
                line=dict(color=color, width=2),
                hoverinfo="none",
                showlegend=False
            ))
            curr_x = [curr_x[-1], new_x[i]]
            curr_y = [curr_y[-1], new_y[i]]
            curr_above = is_above
            
    color = "#00c805" if curr_above else "#ff5000"
    fig.add_trace(go.Scatter(
        x=curr_x, y=curr_y,
        mode="lines",
        line=dict(color=color, width=2),
        hoverinfo="none",
        showlegend=False
    ))
    
    # 4. 隱藏座標軸與背景
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=50,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False, autorange=True),
        showlegend=False
    )
    return fig

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
            
            hist = stock.history(period="1d", interval="15m")
            if not hist.empty:
                fig = create_dynamic_sparkline(hist, prev_close)
                col.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        except Exception:
            col.error(f"{name} 載入失敗")
