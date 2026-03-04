import streamlit as st
import yfinance as yf
from datetime import datetime

# 設定網頁標題與排版
st.set_page_config(page_title="美股最新消息", page_icon="📈", layout="centered")

st.title("📈 最新美股消息整理")
st.write("輸入美股代號，快速獲取最新的市場新聞！")

# 側邊欄：讓使用者輸入股票代號
st.sidebar.header("搜尋設定")
ticker_symbol = st.sidebar.text_input("輸入美股代號 (例如: AAPL, TSLA, NVDA)", value="NVDA").upper()

st.subheader(f"🔍 關於 **{ticker_symbol}** 的最新新聞")

if ticker_symbol:
    try:
        # 取得股票資訊
        stock = yf.Ticker(ticker_symbol)
        news_list = stock.news
        
        if news_list:
            for news in news_list:
                # 【防呆機制】Yahoo Finance 的資料結構可能會變動，我們使用更安全的抓取方式
                # 有時候新聞的真實資料會被包在一層叫做 'content' 的殼裡面
                content = news.get('content', news) 
                
                # 1. 安全取得標題 (找不到就顯示 '無標題')
                title = content.get('title', news.get('title', '無標題'))
                
                # 2. 安全取得連結
                if 'clickThroughUrl' in content:
                    link = content['clickThroughUrl'].get('url', '#')
                else:
                    link = content.get('link', news.get('link', '#'))
                    
                # 3. 安全取得新聞來源
                if 'provider' in content:
                    publisher = content['provider'].get('displayName', '未知來源')
                else:
                    publisher = content.get('publisher', news.get('publisher', '未知來源'))
                
                # 4. 安全處理時間戳記
                pub_time_raw = content.get('pubDate', news.get('providerPublishTime', 0))
                try:
                    # 如果是 Unix Timestamp (數字)
                    if isinstance(pub_time_raw, (int, float)) and pub_time_raw > 0:
                        publish_time = datetime.fromtimestamp(pub_time_raw)
                        time_str = publish_time.strftime('%Y-%m-%d %H:%M:%S')
                    # 如果是 ISO 格式字串 (2024-03-04T12:00:00Z)
                    elif isinstance(pub_time_raw, str):
                        time_str = pub_time_raw[:10] + " " + pub_time_raw[11:19]
                    else:
                        time_str = "未知時間"
                except Exception:
                    time_str = "時間解析錯誤"
                
                # 顯示新聞標題 (附帶超連結)
                st.markdown(f"### [{title}]({link})")
                
                # 顯示新聞來源與時間
                st.caption(f"新聞來源: {publisher} | 發布時間: {time_str}")
                
                # 簡單分隔線
                st.divider()
        else:
            st.warning(f"目前找不到關於 {ticker_symbol} 的新聞。")
            
    except Exception as e:
        st.error("發生錯誤，請確認輸入的股票代號是否正確，或稍後再試。")
        st.error(f"詳細錯誤訊息：{e}")
