import streamlit as st
import requests
import re
import datetime

# 設定頁面資訊
st.set_page_config(page_title="日本旅遊記帳神器", page_icon="💴", layout="centered")

# 注入自訂的 CSS，結合極致的玻璃擬物設計 (Glassmorphism) 與新功能介面
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

html, body {
    font-family: 'Outfit', sans-serif;
}

/* 隱藏預設的主選單與 footer */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* 整體背景 */
.stApp {
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
    color: #f8fafc;
}

/* 主要計算機卡片 (Glassmorphism) 應用在 Streamlit 的 block-container 上 */
[data-testid="block-container"] {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 30px;
    padding: 30px;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
    max-width: 500px;
    margin: 40px auto;
    animation: fadeIn 0.8s ease-out;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

/* 顯示螢幕區域 */
.screen-area {
    background: rgba(0, 0, 0, 0.2);
    border-radius: 20px;
    padding: 20px;
    margin-bottom: 30px;
    text-align: right;
    border: 1px solid rgba(255, 255, 255, 0.05);
    box-shadow: inset 0 2px 10px rgba(0,0,0,0.2);
}

.screen-expr {
    font-size: 1.2rem;
    font-weight: 300;
    color: #94a3b8;
    min-height: 1.8rem;
    word-wrap: break-word;
    margin-bottom: 5px;
}

.screen-jpy {
    font-size: 3.5rem;
    font-weight: 800;
    color: #ffffff;
    line-height: 1.1;
    word-wrap: break-word;
}

.screen-twd {
    font-size: 2rem;
    font-weight: 600;
    margin-top: 5px;
    background: -webkit-linear-gradient(0deg, #38bdf8, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    word-wrap: break-word;
}

/* 狀態標籤 */
.rate-badge {
    background: rgba(56, 189, 248, 0.1);
    color: #38bdf8;
    padding: 8px 16px;
    border-radius: 50px;
    font-size: 0.9rem;
    font-weight: 600;
    display: inline-block;
    border: 1px solid rgba(56, 189, 248, 0.3);
    margin-bottom: 20px;
}

/* 複寫 Streamlit 預設按鈕外觀 (限定在 column 內，避免影響工具列) */
[data-testid="stColumn"] button[data-testid^="stBaseButton"],
button[data-testid="stBaseButton-primary"] {
    width: 100%;
    min-height: 75px;
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    background: rgba(255, 255, 255, 0.05);
    color: white;
    font-size: 1.8rem !important;
    font-weight: 600;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

[data-testid="stColumn"] button[data-testid^="stBaseButton"]:hover,
button[data-testid="stBaseButton-primary"]:hover {
    background: rgba(255, 255, 255, 0.15);
    transform: translateY(-2px);
    border-color: rgba(255, 255, 255, 0.2);
    color: #38bdf8;
}

[data-testid="stColumn"] button[data-testid^="stBaseButton"]:active,
button[data-testid="stBaseButton-primary"]:active {
    transform: translateY(1px);
    background: rgba(255, 255, 255, 0.2);
}

/* 等於按鈕 (Primary) 特別樣式 */
button[data-testid="stBaseButton-primary"] {
    background: linear-gradient(135deg, #38bdf8 0%, #818cf8 100%);
    color: white;
    border: none;
    margin-top: 10px;
}

button[data-testid="stBaseButton-primary"]:hover {
    background: linear-gradient(135deg, #7dd3fc 0%, #a5b4fc 100%);
    color: white !important;
    box-shadow: 0 10px 15px -3px rgba(56, 189, 248, 0.4);
}

/* ================= 手機版響應式優化 (Responsive Design) ================= */
@media (max-width: 600px) {
    /* 讓 Streamlit 的 columns 在手機上「強制保持橫排」，絕對不要變成垂直堆疊 */
    [data-testid="stHorizontalBlock"] {
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 0.5rem !important;
    }
    
    /* 讓每一個 column 在橫排時能平均縮放 */
    [data-testid="stColumn"] {
        width: auto !important;
        flex: 1 1 0% !important;
        min-width: 0 !important;
    }

    /* 手機版：計算機卡片縮小邊距，最大化可視空間 */
    [data-testid="block-container"] {
        padding: 15px 10px !important;
        border-radius: 20px !important;
        margin: 10px auto !important;
        border: none !important; /* 手機上移除多餘邊框 */
    }

    /* 手機版：螢幕字體稍微縮小 */
    .screen-jpy { font-size: 2.8rem; }
    .screen-twd { font-size: 1.5rem; }
    .screen-expr { font-size: 1.1rem; }

    /* 手機版：按鈕稍微變矮、字體稍微縮小，確保 4 欄塞得下 */
    [data-testid="stColumn"] button[data-testid^="stBaseButton"],
    button[data-testid="stBaseButton-primary"] {
        min-height: 60px;
        font-size: 1.5rem !important;
        padding: 0 !important;
    }
}


/* 快速按鈕縮小一點 */
.quick-btn button {
    min-height: 60px !important;
    font-size: 1.2rem !important;
}

/* 縮小按鈕之間的間距 */
[data-testid="column"] {
    padding: 0 4px;
}
</style>
""", unsafe_allow_html=True)

# 使用 cache 抓取匯率，避免每次點按鈕都重新發送網路請求 (快取 1 小時)
@st.cache_data(ttl=3600)
def fetch_exchange_rate():
    try:
        response = requests.get('https://open.er-api.com/v6/latest/JPY')
        data = response.json()
        return data['rates']['TWD']
    except:
        return 0.21 # 發生錯誤時的預設值

exchange_rate = fetch_exchange_rate()

# 初始化計算機記憶體 (狀態)
if 'expr' not in st.session_state:
    st.session_state.expr = ""
if 'jpy_result' not in st.session_state:
    st.session_state.jpy_result = "0"
if 'twd_result' not in st.session_state:
    st.session_state.twd_result = "0"
if 'shopping_list' not in st.session_state:
    st.session_state.shopping_list = []

# 按鈕被點擊時的動作 (callback)
def button_click(val):
    cat = st.session_state.get('cat_input', '')
    raw_note = st.session_state.get('note_input', '')
    note = f"{cat}-{raw_note}" if raw_note else cat

    
    # 當按下運算符號或等於時，如果有備註且最後一個字是數字，就把備註加上去
    if val in ['+', '-', '*', '/', '=']:
        if note and re.search(r'\d$', st.session_state.expr):
            st.session_state.expr += f"({note})"
            st.session_state.note_input = "" # 清空輸入框
            
    if val == 'C':
        st.session_state.expr = ""
        st.session_state.jpy_result = "0"
        st.session_state.twd_result = "0"
        st.session_state.note_input = ""
    elif val == '⌫':
        if len(st.session_state.expr) > 0:
            # 如果最後是帶有括號的備註，例如 "(飲食-拉麵)"，則一併刪除整個備註
            match = re.search(r'\([^)]*\)$', st.session_state.expr)
            if match:
                st.session_state.expr = st.session_state.expr[:match.start()]
            else:
                st.session_state.expr = st.session_state.expr[:-1]
        calculate()
    elif val == '=':
        calculate()
        # 直接抓取算完的總金額進明細
        if st.session_state.expr:
            tz_str = st.session_state.get("tz_input", "🇯🇵 日本 (GMT+9)")
            tz_offset = 9 if "日本" in tz_str else 8
            tz = datetime.timezone(datetime.timedelta(hours=tz_offset))
            current_time = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M")
            
            try:
                # 1. 取得計算機畫面上最終的總結果 (去掉千分位逗號)
                final_amount = float(st.session_state.jpy_result.replace(',', ''))
                
                # 2. 決定這個總金額的名稱：
                # 找出算式裡所有的備註 (例如 100(衣服)+200(褲子))
                notes = re.findall(r'\((.*?)\)', st.session_state.expr)
                
                if notes:
                    # 過濾空白並「去除重複」的備註，例如 ['購物', '購物'] 變成 ['購物']
                    valid_notes = list(dict.fromkeys([n for n in notes if n.strip()]))
                    final_note = "、".join(valid_notes) if valid_notes else "未分類"
                else:
                    # 如果算式裡完全沒有括號，就抓畫面上目前的下拉選單與輸入框
                    cat = st.session_state.get('cat_input', '')
                    raw_note = st.session_state.get('note_input', '')
                    final_note = f"{cat}-{raw_note}" if raw_note else cat
                    if not final_note:
                        final_note = "未分類"
                        
                st.session_state.shopping_list.append({
                    "時間 (可修改)": current_time,
                    "項目 (可修改)": final_note,
                    "日幣金額": final_amount
                })
            except Exception:
                pass
                
            # 清空算式與備註，讓下一筆重新開始
            st.session_state.expr = ""
            st.session_state.show_export = False # 計算後隱藏匯出區域
            st.session_state.note_input = ""
    elif val in ['+1000', '+5000', '+10000']:
        # 快速加總，也可以一併帶入備註
        num = val.replace('+', '')
        item_str = f"{num}({note})" if note else num
        if st.session_state.expr == "":
            st.session_state.expr = item_str
        else:
            # 如果前面已經有數字且沒有運算符號結尾，預設補上 +
            if re.search(r'[\d\)]$', st.session_state.expr):
                st.session_state.expr += f"+{item_str}"
            else:
                st.session_state.expr += item_str
        st.session_state.note_input = ""
        calculate()
    else:
        st.session_state.expr += str(val)
        calculate()

# 計算算式的邏輯
def calculate():
    expr = st.session_state.expr
    if expr == "":
        st.session_state.jpy_result = "0"
        st.session_state.twd_result = "0"
        return
    
    try:
        # 移除備註 (即括號與裡面的內容) 再進行計算
        math_expr = re.sub(r'\(.*?\)', '', expr)
        # 安全處理，只允許數字與數學符號
        sanitized_expr = re.sub(r'[^0-9+\-*/.]', '', math_expr)
        # 如果最後是符號結尾，先不計算
        if sanitized_expr and sanitized_expr[-1] in "+-*/.":
            return
            
        jpy_total = eval(sanitized_expr)
        twd_total = jpy_total * exchange_rate
        
        # 轉成有千分位符號的整數格式
        st.session_state.jpy_result = f"{int(round(jpy_total)):,}"
        st.session_state.twd_result = f"{int(round(twd_total)):,}"
    except Exception:
        pass # 算式不完整時不更新結果

# --- 介面繪製 ---
st.markdown("<div align='center'><h2 style='color: white; margin-bottom: 20px;'>💴 日本旅遊記帳神器</h2></div>", unsafe_allow_html=True)

# 設定與顯示目前時間
with st.expander("⚙️ 系統設定 (時區校正)"):
    st.radio("選擇當地時區", ["🇯🇵 日本 (GMT+9)", "🇹🇼 台灣 (GMT+8)"], key="tz_input", horizontal=True)

tz_str = st.session_state.get("tz_input", "🇯🇵 日本 (GMT+9)")
tz_offset = 9 if "日本" in tz_str else 8
tz = datetime.timezone(datetime.timedelta(hours=tz_offset))
current_display_time = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M")

# 顯示目前的即時匯率標籤與系統時間
st.markdown(f'<div align="center"><div class="rate-badge">🟢 匯率：1 JPY = {exchange_rate:.4f} TWD &nbsp;|&nbsp; 🕒 時間：{current_display_time}</div></div>', unsafe_allow_html=True)

# 顯示螢幕
st_expr = st.session_state.expr
st_jpy = st.session_state.jpy_result
st_twd = st.session_state.twd_result

# 將乘除符號美化顯示
display_expr = st_expr.replace('*', '×').replace('/', '÷')

st.markdown(f"""
<div class="screen-area">
    <div class="screen-expr">{display_expr} {'=' if display_expr else ''}</div>
    <div class="screen-jpy">¥ {st_jpy}</div>
    <div class="screen-twd">NT$ {st_twd}</div>
</div>
""", unsafe_allow_html=True)

# 快速分類與備註
col_c1, col_c2 = st.columns([2, 3])
with col_c1:
    st.selectbox("📌 快速分類", ["🍽️ 飲食", "🚆 交通", "🛍️ 購物", "🏨 住宿", "📝 其他"], key="cat_input")
with col_c2:
    st.text_input("📝 細項備註 (選填)", key="note_input")

# 第一排：快速加總按鈕
st.markdown('<div class="quick-btn">', unsafe_allow_html=True)
col_q1, col_q2, col_q3 = st.columns(3, gap="small")
with col_q1:
    st.button("+1000", key="btn_1k", use_container_width=True, on_click=button_click, args=('+1000',))
with col_q2:
    st.button("+5000", key="btn_5k", use_container_width=True, on_click=button_click, args=('+5000',))
with col_q3:
    st.button("+10000", key="btn_10k", use_container_width=True, on_click=button_click, args=('+10000',))
st.markdown('</div>', unsafe_allow_html=True)

st.write("") # 留白

# 計算機主鍵盤區塊
col1, col2, col3, col4 = st.columns(4, gap="small")

with col1:
    st.button("C", use_container_width=True, on_click=button_click, args=('C',))
    st.button("7", use_container_width=True, on_click=button_click, args=('7',))
    st.button("4", use_container_width=True, on_click=button_click, args=('4',))
    st.button("1", use_container_width=True, on_click=button_click, args=('1',))
    st.button("00", use_container_width=True, on_click=button_click, args=('00',))

with col2:
    st.button("(", use_container_width=True, on_click=button_click, args=('(',))
    st.button("8", use_container_width=True, on_click=button_click, args=('8',))
    st.button("5", use_container_width=True, on_click=button_click, args=('5',))
    st.button("2", use_container_width=True, on_click=button_click, args=('2',))
    st.button("0", use_container_width=True, on_click=button_click, args=('0',))

with col3:
    st.button(")", use_container_width=True, on_click=button_click, args=(')',))
    st.button("9", use_container_width=True, on_click=button_click, args=('9',))
    st.button("6", use_container_width=True, on_click=button_click, args=('6',))
    st.button("3", use_container_width=True, on_click=button_click, args=('3',))
    st.button(".", use_container_width=True, on_click=button_click, args=('.',))

with col4:
    st.button("⌫", use_container_width=True, on_click=button_click, args=('⌫',))
    st.button("÷", use_container_width=True, on_click=button_click, args=('/',))
    st.button("×", use_container_width=True, on_click=button_click, args=('*',))
    st.button("-", use_container_width=True, on_click=button_click, args=('-',))
    st.button("+", use_container_width=True, on_click=button_click, args=('+',))

# 將等於按鈕獨立出來，做成超級大按鈕
st.button("=", type="primary", use_container_width=True, on_click=button_click, args=('=',))

# --- 購物清單明細 (記帳功能) ---
st.markdown("---")
st.markdown("<h3 style='color: #f8fafc; font-size: 1.2rem;'>🧾 購物清單明細 (可直接點擊表格編輯/刪除/新增)</h3>", unsafe_allow_html=True)

if not st.session_state.shopping_list:
    st.markdown("<div style='color: #64748b;'>目前還沒有項目喔！請在上方輸入金額與備註後，按下「=」將項目加入明細。</div>", unsafe_allow_html=True)
else:
    # 準備顯示用的清單 (動態計算台幣)
    display_list = []
    for item in st.session_state.shopping_list:
        display_item = item.copy()
        if item.get("日幣金額") is not None:
            display_item["台幣金額 (約略)"] = int(round(item["日幣金額"] * exchange_rate))
        else:
            display_item["台幣金額 (約略)"] = None
        display_list.append(display_item)
        
    # 使用 st.data_editor 讓表格可編輯
    edited_list = st.data_editor(
        display_list,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        column_config={
            "時間 (可修改)": st.column_config.TextColumn(
                "時間",
                width="small"
            ),
            "項目 (可修改)": st.column_config.TextColumn(
                "項目 (可修改)",
                required=True
            ),
            "日幣金額": st.column_config.NumberColumn(
                "日幣金額",
                min_value=0,
                format="¥ %d",
                required=True
            ),
            "台幣金額 (約略)": st.column_config.NumberColumn(
                "台幣 (參考)",
                format="NT$ %d",
                disabled=True # 台幣是動態算出來的，不開放修改
            )
        }
    )
    
    # 將編輯後的清單存回 session_state (只存日幣原始資料)
    new_shopping_list = []
    for item in edited_list:
        new_shopping_list.append({
            "時間 (可修改)": item.get("時間 (可修改)", ""),
            "項目 (可修改)": item.get("項目 (可修改)", "未分類"),
            "日幣金額": item.get("日幣金額")
        })
    st.session_state.shopping_list = new_shopping_list
    
    # 加總所有購物清單的金額
    total_jpy = sum(item["日幣金額"] for item in edited_list if item.get("日幣金額") is not None)
    total_twd = int(round(total_jpy * exchange_rate))
    
    st.markdown(f"<div style='margin-top: 15px; padding: 15px; background: rgba(56,189,248,0.1); border-radius: 10px; border: 1px solid rgba(56,189,248,0.3);'>"
                f"<h4 style='color: #38bdf8; margin:0;'>💰 清單總計：¥ {int(total_jpy):,} <span style='font-size: 1rem; color: #94a3b8;'>(約 NT$ {total_twd:,})</span></h4>"
                f"</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("📋", help="產生純文字明細，方便一鍵複製並貼上至手機備忘錄"):
        st.session_state.show_export = True
        
    if st.session_state.get("show_export", False):
        tz_str = st.session_state.get("tz_input", "🇯🇵 日本 (GMT+9)")
        tz_offset = 9 if "日本" in tz_str else 8
        tz = datetime.timezone(datetime.timedelta(hours=tz_offset))
        current_date = datetime.datetime.now(tz).strftime('%Y-%m-%d')
        
        export_text = f"【日本旅遊記帳明細 | {current_date}】\n"
        export_text += "-" * 25 + "\n"
        for item in st.session_state.shopping_list:
            if item.get("日幣金額") is not None:
                twd = int(round(item["日幣金額"] * exchange_rate))
                time_str = item.get("時間 (可修改)", "")
                time_prefix = f"[{time_str.split()[-1]}] " if time_str else ""
                export_text += f"{time_prefix}{item['項目 (可修改)']}: ¥{int(item['日幣金額'])} (NT${twd})\n"
        export_text += "-" * 25 + "\n"
        export_text += f"總計: ¥{int(total_jpy)} (約 NT${total_twd})\n"
        
        st.info("👇 請點擊下方區塊右上角的複製圖示")
        st.code(export_text, language="markdown")

