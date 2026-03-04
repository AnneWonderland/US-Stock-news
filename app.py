import streamlit as st
import yfinance as yf
import google.generativeai as genai
import requests
from datetime import datetime, timedelta

# 設定網頁標題與排版
st.set_page_config(page_title="專業級 AI 美股情報站", page_icon="🏦", layout="centered")

st.title("🏦 專業級 AI 美股情報站")
st.write("串接華爾街機構級資訊源，過濾雜訊，只看真正有價值的重點！")

# 側邊欄：搜尋設定
st.sidebar.header("搜尋設定")
ticker_symbol = st.sidebar.text_input("輸入美股代號 (例如: AAPL, TSLA, NVDA)", value="NVDA").upper()

# 【新增功能】讓使用者自己決定要看幾篇新聞
news_count = st.sidebar.slider("選擇要顯示的新聞數量", min_value=1, max_value=10, value=5)

# --- 驗證與設定 API 金鑰 ---
api_ready = False
try:
    # 讀取 Gemini 金鑰
    gemini_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # 讀取 Finnhub 金鑰
    finnhub_key = st.secrets["FINNHUB_API_KEY"]
    
    api_ready = True
except Exception as e:
    st.error("⚠️ 找不到 API 金鑰！請確認 Secrets 中已設定 `GEMINI_API_KEY` 與 `FINNHUB_API_KEY`。")

# --- AI 分析專用功能 ---
def analyze_news_with_ai(title, summary, publisher):
    prompt = f"""
    你是一位華爾街資深分析師。請根據以下專業財經新聞的標題與摘要，判斷對該公司股價的短期影響。
    新聞標題：{title}
    新聞摘要：{summary}
    新聞來源：{publisher}
    
    請嚴格按照以下格式回覆（不要加入其他的問候語或解釋）：
    【判斷】：利多 / 利空 / 中立 (只能選擇一個)
    【情緒分數】：1~10分 (1代表最悲觀，10代表最樂觀)
    【重點總結】：用繁體中文，將這則新聞對投資人的意義濃縮成一句話。
    """
    try:
        response = model.generate_content(
            prompt,
            safety_settings=[
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
            ]
        )
        return response.text
    except Exception as e:
        return f"❌ AI 拒絕回答或發生錯誤，真實原因：{e}"

st.subheader(f"🔍 關於 **{ticker_symbol}** 的精選情報")

if ticker_symbol and api_ready:
    try:
        st.info(f"🔄 正在為您抓取最新 {news_count} 筆高品質新聞，並請 AI 進行深度解讀...")
        
        # 設定抓取過去 7 天內的新聞
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        # 呼叫 Finnhub 專業新聞 API
        url = f"https://finnhub.io/api/v1/company-news?symbol={ticker_symbol}&from={start_date}&to={end_date}&token={finnhub_key}"
        response = requests.get(url)
        news_list = response.json()
        
        # 確保回傳的是清單型態的資料
        if isinstance(news_list, list) and len(news_list) > 0:
            
            # 【關鍵修改】不再寫死 3 篇，而是根據你在側邊欄拉動的數量 (news_count) 來顯示
            for news in news_list[:news_count]:
                # 抓取 Finnhub 提供的精確欄位
                title = news.get('headline', '無標題')
                summary = news.get('summary', '無摘要')
                link = news.get('url', '#')
                publisher = news.get('source', '未知來源')
                
                # 處理時間 (Finnhub 提供的是 Unix Timestamp)
                timestamp = news.get('datetime', 0)
                if timestamp > 0:
                    time_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                else:
                    time_str = "發布時間未知"
                
                # 顯示新聞標題
                st.markdown(f"### [{title}]({link})")
                st.caption(f"新聞來源: {publisher} | 發布時間: {time_str}")
                
                # 將「標題」與「摘要」一起丟給 AI 分析
                if title != '無標題':
                    ai_result = analyze_news_with_ai(title, summary, publisher)
                    if "❌" in ai_result:
                        st.error(ai_result)
                    else:
                        st.success(ai_result)
                
                st.divider()
                
            st.caption(f"✅ 備註：目前資料來源為華爾街機構級 API (Finnhub)，為維持品質與效能，最多顯示近期 {news_count} 則重大情報。")
        else:
            st.warning(f"目前資料庫中找不到關於 {ticker_symbol} 近期的高價值新聞。這通常代表該公司最近沒有重大事件，或是輸入了錯誤的代號。")
            
    except Exception as e:
        st.error("系統連線發生未預期的錯誤，請稍後再試。")
        st.error(f"詳細錯誤訊息：{e}")
