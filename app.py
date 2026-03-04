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
                # 處理時間戳記
                publish_time = datetime.fromtimestamp(news.get('providerPublishTime', 0))
                time_str = publish_time.strftime('%Y-%m-%d %H:%M:%S')
                
                # 顯示新聞標題 (附帶超連結)
                st.markdown(f"### [{news['title']}]({news['link']})")
                
                # 顯示新聞來源與時間
                st.caption(f"新聞來源: {news['publisher']} | 發布時間: {time_str}")
                
                # 簡單分隔線
                st.divider()
        else:
            st.warning(f"目前找不到關於 {ticker_symbol} 的新聞。")
            
  except Exception as e:
        st.error("發生錯誤，請確認輸入的股票代號是否正確，或稍後再試。")
        st.error(f"詳細錯誤訊息：{e}") # 加入這行來顯示真實的系統錯誤
        st.exception(e) # 這行可以印出完整的錯誤追蹤 (Traceback)，方便除錯
