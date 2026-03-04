import streamlit as st
import yfinance as yf
import google.generativeai as genai
from datetime import datetime

# 設定網頁標題與排版
st.set_page_config(page_title="AI 美股情報站", page_icon="🤖", layout="centered")

st.title("🤖 AI 美股情報站 (增強版)")
st.write("不只抓新聞，更讓 AI 直接幫你劃重點、判斷多空！")

# 側邊欄：讓使用者輸入股票代號
st.sidebar.header("搜尋設定")
ticker_symbol = st.sidebar.text_input("輸入美股代號 (例如: AAPL, TSLA, NVDA)", value="NVDA").upper()

# --- 驗證與設定 Gemini API ---
api_ready = False
try:
    # 嘗試從 Streamlit 保險箱中拿出鑰匙
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    # 使用 Google 最新且反應最快的 flash 模型
    model = genai.GenerativeModel('gemini-1.5-flash')
    api_ready = True
except Exception as e:
    st.error("⚠️ 找不到 Gemini API Key！請確認是否已在 Streamlit 的 Settings -> Secrets 中設定 `GEMINI_API_KEY`。")

# --- AI 分析專用功能 ---
def analyze_news_with_ai(title, publisher):
    prompt = f"""
    你是一位專業的華爾街股市分析師。請根據以下這則財經新聞標題與來源，判斷對該公司股價的短期影響。
    新聞標題：{title}
    新聞來源：{publisher}
    
    請嚴格按照以下格式回覆（不要加入其他的問候語或解釋）：
    【判斷】：利多 / 利空 / 中立 (只能選擇一個)
    【情緒分數】：1~10分 (1代表最悲觀，10代表最樂觀)
    【重點總結】：用繁體中文，將這則新聞對投資人的意義濃縮成一句話。
    """
    try:
        # 【關鍵修改】手動降低 AI 的安全審查，避免財經新聞的軍事/衝突字眼被誤殺
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
        # 這次我們不藏了，如果 AI 再報錯，直接把真實原因印在畫面上！
        return f"❌ AI 拒絕回答或發生錯誤，真實原因：{e}"

st.subheader(f"🔍 關於 **{ticker_symbol}** 的最新 AI 分析")

if ticker_symbol:
    if api_ready:
        try:
            st.info("🔄 正在請 AI 大師解讀最新新聞，這需要幾秒鐘的時間...")
            stock = yf.Ticker(ticker_symbol)
            news_list = stock.news
            
            if news_list and isinstance(news_list, list):
                valid_news = [n for n in news_list if isinstance(n, dict) and n]
                
                if valid_news:
                    # 為了避免等太久，我們只請 AI 分析最新的 3 則新聞
                    for news in valid_news[:3]:
                        content = news.get('content')
                        if not isinstance(content, dict):
                            content = news 
                            
                        title = str(content.get('title', news.get('title', '無標題')))
                        if title == 'None' or not title.strip():
                            title = '無標題'
                            
                        link = '#'
                        if 'clickThroughUrl' in content and isinstance(content['clickThroughUrl'], dict):
                            link = str(content['clickThroughUrl'].get('url', '#'))
                        else:
                            link = str(content.get('link', news.get('link', '#')))
                            
                        publisher = '未知來源'
                        if 'provider' in content and isinstance(content['provider'], dict):
                            publisher = str(content['provider'].get('displayName', '未知來源'))
                        else:
                            publisher = str(content.get('publisher', news.get('publisher', '未知來源')))
                        
                        # 顯示新聞標題
                        if link != '#' and link != 'None':
                            st.markdown(f"### [{title}]({link})")
                        else:
                            st.markdown(f"### {title}")
                        
                        st.caption(f"新聞來源: {publisher}")
                        
                        # 把新聞丟給 AI 分析並顯示結果
                        if title != '無標題':
                            ai_result = analyze_news_with_ai(title, publisher)
                            # 如果包含錯誤符號就顯示紅色警告，成功則顯示綠色
                            if "❌" in ai_result:
                                st.error(ai_result)
                            else:
                                st.success(ai_result)
                            
                        st.divider()
                        
                    st.caption("✅ 備註：為維持系統效能，目前僅顯示並由 AI 分析最新 3 則新聞。")
                else:
                    st.warning(f"目前沒有 {ticker_symbol} 的有效新聞資料。")
            else:
                st.warning(f"目前找不到關於 {ticker_symbol} 的新聞。")
                
        except Exception as e:
            st.error("系統發生未預期的錯誤，請稍後再試。")
            st.error(f"詳細錯誤訊息：{e}")
    else:
        st.warning("等待 API 金鑰設定中...")
