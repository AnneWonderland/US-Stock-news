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
        
        # 【終極防護 1】確保抓回來的資料是一個清單，而且不是空的
        if news_list and isinstance(news_list, list):
            
            # 【終極防護 2】無情過濾掉所有 Yahoo 塞進來的「空殼」或「非字典」的髒資料
            valid_news = [n for n in news_list if isinstance(n, dict) and n]
            
            if valid_news:
                for news in valid_news:
                    # 【終極防護 3】確保 content 存在且是安全的字典格式
                    content = news.get('content')
                    if not isinstance(content, dict):
                        content = news 
                        
                    # 1. 安全取得標題 (轉成字串防呆)
                    title = str(content.get('title', news.get('title', '無標題')))
                    if title == 'None' or not title.strip():
                        title = '無標題'
                        
                    # 2. 安全取得連結
                    link = '#'
                    if 'clickThroughUrl' in content and isinstance(content['clickThroughUrl'], dict):
                        link = str(content['clickThroughUrl'].get('url', '#'))
                    else:
                        link = str(content.get('link', news.get('link', '#')))
                        
                    # 3. 安全取得新聞來源
                    publisher = '未知來源'
                    if 'provider' in content and isinstance(content['provider'], dict):
                        publisher = str(content['provider'].get('displayName', '未知來源'))
                    else:
                        publisher = str(content.get('publisher', news.get('publisher', '未知來源')))
                    
                    # 4. 安全處理時間戳記
                    time_str = "發布時間未知"
                    pub_time_raw = content.get('pubDate', news.get('providerPublishTime'))
                    
                    try:
                        # 如果是數字格式 (Unix Timestamp)
                        if isinstance(pub_time_raw, (int, float)):
                            # 有些時間會多給毫秒，太長的話要除以1000
                            if pub_time_raw > 1e11: 
                                pub_time_raw = pub_time_raw / 1000
                            time_str = datetime.fromtimestamp(pub_time_raw).strftime('%Y-%m-%d %H:%M:%S')
                        # 如果是字串格式
                        elif isinstance(pub_time_raw, str) and len(pub_time_raw) >= 19:
                            time_str = pub_time_raw[:10] + " " + pub_time_raw[11:19]
                    except Exception:
                        pass # 時間解析失敗就隨它去，維持預設字眼
                    
                    # 顯示新聞標題
                    if link != '#' and link != 'None':
                        st.markdown(f"### [{title}]({link})")
                    else:
                        st.markdown(f"### {title}")
                    
                    # 顯示新聞來源與時間
                    st.caption(f"新聞來源: {publisher} | {time_str}")
                    st.divider()
            else:
                st.warning(f"目前沒有 {ticker_symbol} 的有效新聞資料。")
        else:
            st.warning(f"目前找不到關於 {ticker_symbol} 的新聞。")
            
    except Exception as e:
        st.error("系統發生未預期的錯誤，請稍後再試。")
        st.error(f"詳細錯誤訊息：{e}")
