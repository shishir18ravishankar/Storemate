from supabase import create_client
import streamlit as st
import os
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize supabase client only when values look valid; otherwise keep it None
supabase = None
if SUPABASE_URL and SUPABASE_URL.startswith("http") and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        supabase = None
        try:
            st.error(f"Supabase init failed: {e}")
        except Exception:
            pass
else:
    try:
        st.warning("Supabase not configured. Set SUPABASE_URL and SUPABASE_KEY in Streamlit secrets or environment.")
    except Exception:
        pass
from groq import Groq
import json
from datetime import datetime, timedelta
import base64

# ---- PAGE CONFIG ----
st.set_page_config(page_title="StoreMate", page_icon="🛒", layout="wide")

# ---- CUSTOM CSS ----
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700&family=DM+Sans:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
h1, h2, h3, .stTabs [data-baseweb="tab"] {
    font-family: 'Sora', sans-serif;
}

/* App background */
.stApp { background: #0f1117; color: #f0f0f0; }

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    background: #1a1d27;
    border-radius: 16px;
    padding: 6px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #888;
    border-radius: 12px;
    font-size: 15px;
    font-weight: 500;
    padding: 10px 24px;
    transition: all 0.2s;
}
.stTabs [aria-selected="true"] {
    background: #6C63FF !important;
    color: white !important;
}

/* Metric cards */
[data-testid="metric-container"] {
    background: #1a1d27;
    border-radius: 16px;
    padding: 16px;
    border: 1px solid #2a2d3a;
}
[data-testid="stMetricValue"] { color: #f0f0f0 !important; font-family: 'Sora', sans-serif; }
[data-testid="stMetricLabel"] { color: #888 !important; }
[data-testid="stMetricDelta"] { font-size: 13px !important; }

/* Chat message bubbles */
.user-bubble {
    background: #6C63FF;
    color: white;
    padding: 12px 18px;
    border-radius: 18px 18px 4px 18px;
    margin: 8px 0 8px auto;
    max-width: 75%;
    font-size: 15px;
    line-height: 1.5;
}
.ai-bubble {
    background: #1a1d27;
    color: #f0f0f0;
    padding: 12px 18px;
    border-radius: 18px 18px 18px 4px;
    margin: 8px auto 8px 0;
    max-width: 80%;
    font-size: 15px;
    line-height: 1.5;
    border: 1px solid #2a2d3a;
}
.chat-time {
    font-size: 11px;
    color: #555;
    margin-top: 4px;
}

/* Voice button */
.voice-btn {
    background: linear-gradient(135deg, #6C63FF, #5a54e0);
    color: white;
    border: none;
    border-radius: 50px;
    padding: 12px 28px;
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;
    font-family: 'Sora', sans-serif;
    transition: all 0.2s;
}
.voice-btn:hover { transform: scale(1.03); }

/* Table styling */
.stDataFrame {
    background: #1a1d27 !important;
    border-radius: 12px;
}

/* Alert boxes */
.alert-danger {
    background: #2a1a1a;
    border-left: 4px solid #e74c3c;
    padding: 12px 16px;
    border-radius: 0 12px 12px 0;
    margin: 8px 0;
    color: #f5a5a5;
}
.alert-success {
    background: #1a2a1a;
    border-left: 4px solid #2ecc71;
    padding: 12px 16px;
    border-radius: 0 12px 12px 0;
    margin: 8px 0;
    color: #a5f5b5;
}
.alert-warning {
    background: #2a2210;
    border-left: 4px solid #f39c12;
    padding: 12px 16px;
    border-radius: 0 12px 12px 0;
    margin: 8px 0;
    color: #f5d5a5;
}

/* Section headers */
.section-header {
    font-family: 'Sora', sans-serif;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #6C63FF;
    margin: 20px 0 10px 0;
}

/* Analysis card */
.analysis-card {
    background: #1a1d27;
    border: 1px solid #2a2d3a;
    border-radius: 16px;
    padding: 20px 24px;
    margin: 12px 0;
    line-height: 1.7;
    color: #d0d0d0;
}

/* Weekly badge */
.badge-weekly {
    background: #2d1f6e;
    color: #a99df7;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    display: inline-block;
    margin-bottom: 10px;
}
.badge-daily {
    background: #1a2e1a;
    color: #7ee89a;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    display: inline-block;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# ---- GROQ CLIENT ----
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

# ---- SESSION STATE ----
defaults = {
    "messages": [],
    "transactions": [],
    "daily_summary": "",
    "weekly_summary": "",
    "last_analysis_count": 0,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ---- SYSTEM PROMPT ----
SYSTEM_PROMPT = """You are StoreMate, an AI assistant for small retail shop owners.
The owner may speak in simple English or describe an image.
Extract ALL transactions from their message and return ONLY a valid JSON object like this:

{
    "transactions": [
        {"type": "sale", "product": "Chips", "quantity": 5, "price_per_unit": 20, "total": 100},
        {"type": "purchase", "product": "Biscuits", "quantity": 10, "price_per_unit": 5, "total": 50}
    ],
    "reply": "Got it! You sold 5 packets of chips for ₹100. Biscuits purchased for ₹50. Today's profit: ₹50. Keep going! 💪"
}

If user message has no transactions (just a question), return:
{"transactions": [], "reply": "Your friendly response here"}

Rules:
- reply should be in simple, friendly English
- Always calculate correct totals
- return ONLY valid JSON, nothing else, no markdown, no backticks"""

# ---- FUNCTIONS ----
def get_ai_response(user_message):
    try:
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3,
            max_tokens=800
        )
        raw = resp.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except Exception as e:
        return {
            "transactions": [],
            "reply": f"Sorry, something went wrong. Please try again! ({str(e)[:60]})"
        }
def get_daily_analysis():
    if not st.session_state.transactions:
        return "No transactions yet. Add sales or purchases in the chat!"
    total_sales = sum(t['total'] for t in st.session_state.transactions if t['type'] == 'sale')
    total_purchases = sum(t['total'] for t in st.session_state.transactions if t['type'] == 'purchase')
    profit = total_sales - total_purchases
    prompt = f"""You are a friendly business advisor for small retail shop owners.
Transactions today: {json.dumps(st.session_state.transactions)}
Total sales: ₹{total_sales}, Total purchases: ₹{total_purchases}, Net profit: ₹{profit}

Give a daily business summary with:
1. Today's performance (profit/loss, top selling items)
2. What stocks are running low and need refilling
3. Three practical tips to improve sales for a small shop
Keep the tone warm, simple and encouraging. Use plain English. Max 200 words."""
    try:
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400
        )
        return resp.choices[0].message.content
    except:
        return "Analysis generate nahi ho saka. Thodi der baad try karo!"

def get_weekly_analysis():
    if not st.session_state.transactions:
        return "Add some transactions first to get a weekly analysis!"
    total_sales = sum(t['total'] for t in st.session_state.transactions if t['type'] == 'sale')
    total_purchases = sum(t['total'] for t in st.session_state.transactions if t['type'] == 'purchase')
    profit = total_sales - total_purchases
    products = {}
    for t in st.session_state.transactions:
        p = t['product']
        products[p] = products.get(p, 0) + (t['total'] if t['type'] == 'sale' else 0)
    top_products = sorted(products.items(), key=lambda x: x[1], reverse=True)[:5]
    prompt = f"""You are a business advisor for a small retail shop.
This week's data: {json.dumps(st.session_state.transactions)}
Total sales: ₹{total_sales}, Purchases: ₹{total_purchases}, Profit: ₹{profit}
Top products by revenue: {top_products}

Give a weekly business review with:
1. Weekly performance summary
2. Best selling products — suggest stocking more of these
3. Slow moving items — suggest discounting or reducing orders
4. Three practical strategies to grow the business next week
Keep it practical, friendly and motivating. Use simple English. Max 250 words."""
    try:
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        return resp.choices[0].message.content
    except:
        return "Weekly analysis generate nahi ho saka!"

def get_stock_levels():
    stock = {}
    for t in st.session_state.transactions:
        p = t['product']
        if p not in stock:
            stock[p] = 0
        if t['type'] == 'purchase':
            stock[p] += t['quantity']
        else:
            stock[p] -= t['quantity']
    return stock

def auto_refresh_analysis():
    count = len(st.session_state.transactions)
    if count != st.session_state.last_analysis_count and count > 0:
        st.session_state.daily_summary = get_daily_analysis()
        st.session_state.last_analysis_count = count

# ---- HEADER ----
st.markdown("""
<div style="padding: 24px 0 8px 0;">
  <h1 style="font-family:'Sora',sans-serif; font-size:32px; font-weight:700; margin:0; color:#f0f0f0;">
    🛒 StoreMate
  </h1>
    <p style="color:#888; margin:4px 0 0 0; font-size:15px;">Your AI shop assistant — use voice, image, or text!</p>
</div>
""", unsafe_allow_html=True)

# Auto-refresh analysis when new transactions come in
auto_refresh_analysis()

# ---- TABS ----
tab1, tab2, tab3 = st.tabs(["💬  Chat", "📦  Data Store", "📊  Analysis"])

# ==================== TAB 1: CHAT ====================
with tab1:
    # Voice Input
    st.markdown('<div class="section-header">🎤 Voice Message</div>', unsafe_allow_html=True)
    st.components.v1.html("""
    <div style="font-family:'DM Sans',sans-serif; padding:4px 0 12px 0;">
      <div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap;">
                <button onclick="startRec()" id="startBtn"
          style="background:#6C63FF;color:white;padding:11px 22px;border:none;border-radius:50px;cursor:pointer;font-size:14px;font-weight:600;font-family:'DM Sans',sans-serif;">
                    🎤 Start Speaking
        </button>
                <button onclick="stopRec()" id="stopBtn" disabled
          style="background:#333;color:#ccc;padding:11px 22px;border:none;border-radius:50px;cursor:pointer;font-size:14px;font-weight:600;font-family:'DM Sans',sans-serif;">
                    ⏹ Stop
        </button>
                <span id="status" style="color:#888;font-size:13px;">Press Start and speak in English</span>
      </div>
      <div id="resultBox" style="display:none; margin-top:12px; background:#1a1d27; border:1px solid #2a2d3a; border-radius:12px; padding:14px 16px;">
        <p style="color:#888;font-size:12px;margin:0 0 6px 0;text-transform:uppercase;letter-spacing:1px;">You said:</p>
        <p id="resultText" style="color:#f0f0f0;font-size:15px;margin:0;line-height:1.5;"></p>
        <p style="color:#888;font-size:12px;margin:10px 0 0 0;">👆 Copy this text and paste it in the chat box below</p>
      </div>
    </div>
    <script>
      let rec;
      function startRec() {
        rec = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        rec.lang = 'en-US';
        rec.continuous = false;
        rec.interimResults = false;
                rec.onstart = () => {
                    document.getElementById('status').innerText = '🔴 Recording... please speak now!';
          document.getElementById('startBtn').disabled = true;
          document.getElementById('stopBtn').disabled = false;
          document.getElementById('stopBtn').style.background = '#e74c3c';
          document.getElementById('stopBtn').style.color = 'white';
        };
        rec.onresult = (e) => {
          const text = e.results[0][0].transcript;
          document.getElementById('resultText').innerText = text;
          document.getElementById('resultBox').style.display = 'block';
                    document.getElementById('status').innerText = '✅ Done! Copy text above and paste in chat below ↓';
        };
                rec.onerror = (e) => {
                    document.getElementById('status').innerText = '❌ Error: ' + e.error + ' — please type below';
                };
        rec.onend = () => {
          document.getElementById('startBtn').disabled = false;
          document.getElementById('stopBtn').disabled = true;
          document.getElementById('stopBtn').style.background = '#333';
          document.getElementById('stopBtn').style.color = '#ccc';
        };
        rec.start();
      }
      function stopRec() { if (rec) rec.stop(); }
    </script>
    """, height=180)

    # Image Upload
    st.markdown('<div class="section-header">📷 Upload Bill or Stock Sheet</div>', unsafe_allow_html=True)
    uploaded_img = st.file_uploader(
        "Bill, stock list, ya haath se likha koi bhi kaagaz upload karo",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed"
    )
    if uploaded_img:
        col_img, col_tip = st.columns([1, 2])
        with col_img:
            st.image(uploaded_img, width=200)
        with col_tip:
            st.markdown("""
                <div style="background:#1a2a1a; border-left:4px solid #2ecc71; padding:12px 16px; border-radius:0 12px 12px 0; color:#a5f5b5; font-size:14px;">
                    ✅ Image uploaded!<br><br>
                    Now type below what this image is — for example:<br>
                    <em>"this is today's sales bill"</em> or<br>
                    <em>"this is my stock list"</em>
                    </div>
            """, unsafe_allow_html=True)

    # Chat History
    st.markdown('<div class="section-header">✍️ Chat</div>', unsafe_allow_html=True)

    chat_container = st.container()
    with chat_container:
        if not st.session_state.messages:
            st.markdown("""
            <div style="text-align:center; padding:30px 0; color:#555;">
              <p style="font-size:28px; margin:0;">🛒</p>
              <p style="font-size:16px; margin:8px 0 4px 0; color:#888;">StoreMate is ready!</p>
              <p style="font-size:14px; color:#555;">Tell me what you sold or purchased — by voice, image, or type here</p>
            </div>
            """, unsafe_allow_html=True)

        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f"""
                <div style="display:flex; justify-content:flex-end; margin:6px 0;">
                  <div class="user-bubble">{msg["content"]}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="display:flex; justify-content:flex-start; margin:6px 0;">
                  <div class="ai-bubble">🤖 {msg["content"]}</div>
                </div>
                """, unsafe_allow_html=True)

    # Chat Input
    user_input = st.chat_input("Type or paste voice text — e.g. 'sold 5 chips at 20 each, bought 10 biscuits at 5 each'")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.spinner("🤔 Samajh raha hoon..."):
            data = get_ai_response(user_input)
            reply = data.get("reply", "Got it!")
            new_txns = data.get("transactions", [])

            for t in new_txns:
                t["time"] = datetime.now().strftime("%H:%M")
                t["date"] = datetime.now().strftime("%Y-%m-%d")

            st.session_state.transactions.extend(new_txns)
            st.session_state.messages.append({"role": "assistant", "content": reply})

            # Auto-refresh analysis
            if new_txns:
                st.session_state.daily_summary = get_daily_analysis()
                st.session_state.last_analysis_count = len(st.session_state.transactions)

        st.rerun()

# ==================== TAB 2: DATA STORE ====================
with tab2:
    if not st.session_state.transactions:
                st.markdown("""
                <div style="text-align:center; padding:50px 0; color:#555;">
                    <p style="font-size:40px; margin:0;">📦</p>
                    <p style="font-size:16px; margin:12px 0 6px 0; color:#888;">No transactions yet</p>
                    <p style="font-size:14px; color:#555;">Go to the Chat tab and add sales or purchases</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        sales = [t for t in st.session_state.transactions if t['type'] == 'sale']
        purchases = [t for t in st.session_state.transactions if t['type'] == 'purchase']
        total_sales = sum(t['total'] for t in sales)
        total_purchases = sum(t['total'] for t in purchases)
        profit = total_sales - total_purchases

        # Summary metrics
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("💰 Total Sales", f"₹{total_sales}")
        c2.metric("🛒 Total Purchases", f"₹{total_purchases}")
        c3.metric("📈 Net Profit", f"₹{profit}", delta=f"₹{profit}")
        c4.metric("🔢 Transactions", len(st.session_state.transactions))

        # Stock levels
        st.markdown('<div class="section-header">📊 Current Stock Levels</div>', unsafe_allow_html=True)
        stock_levels = get_stock_levels()
        if stock_levels:
            cols = st.columns(min(len(stock_levels), 4))
            for i, (product, qty) in enumerate(stock_levels.items()):
                with cols[i % 4]:
                    color = "🔴" if qty <= 0 else "🟡" if qty < 5 else "🟢"
                    st.metric(f"{color} {product}", f"{qty} units")

        # Sales table
        st.markdown('<div class="section-header">📤 Sales Today</div>', unsafe_allow_html=True)
        if sales:
            st.dataframe(
                sales,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "type": st.column_config.TextColumn("Type"),
                    "product": st.column_config.TextColumn("Product"),
                    "quantity": st.column_config.NumberColumn("Qty"),
                    "price_per_unit": st.column_config.NumberColumn("Price/Unit (₹)"),
                    "total": st.column_config.NumberColumn("Total (₹)"),
                    "time": st.column_config.TextColumn("Time"),
                }
            )
        else:
            st.info("No sales recorded yet")

        # Purchases table
        st.markdown('<div class="section-header">📥 Purchases Today</div>', unsafe_allow_html=True)
        if purchases:
            st.dataframe(
                purchases,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "type": st.column_config.TextColumn("Type"),
                    "product": st.column_config.TextColumn("Product"),
                    "quantity": st.column_config.NumberColumn("Qty"),
                    "price_per_unit": st.column_config.NumberColumn("Price/Unit (₹)"),
                    "total": st.column_config.NumberColumn("Total (₹)"),
                    "time": st.column_config.TextColumn("Time"),
                }
            )
        else:
            st.info("No purchases recorded yet")

        # Clear button
        st.markdown("---")
        if st.button("🗑️ Clear All Transactions (New Day)", type="secondary"):
            st.session_state.transactions = []
            st.session_state.messages = []
            st.session_state.daily_summary = ""
            st.session_state.weekly_summary = ""
            st.session_state.last_analysis_count = 0
            st.rerun()

# ==================== TAB 3: ANALYSIS ====================
with tab3:
    today = datetime.now()
    is_weekend = today.weekday() in [4, 5]  # Friday=4, Saturday=5
    if not st.session_state.transactions:
        st.markdown("""
        <div style="text-align:center; padding:50px 0; color:#555;">
          <p style="font-size:40px; margin:0;">📊</p>
          <p style="font-size:16px; margin:12px 0 6px 0; color:#888;">Transactions needed for analysis</p>
          <p style="font-size:14px; color:#555;">First go to the Chat tab and add today's data</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        col_a, col_b = st.columns([1, 1])
        with col_a:
            if st.button("🔄 Refresh Daily Summary", use_container_width=True):
                with st.spinner("AI analysis kar raha hai..."):
                    st.session_state.daily_summary = get_daily_analysis()
                    st.session_state.last_analysis_count = len(st.session_state.transactions)
        with col_b:
            if st.button("📅 Get Weekly Summary", use_container_width=True, disabled=not is_weekend):
                with st.spinner("Generating weekly report..."):
                    st.session_state.weekly_summary = get_weekly_analysis()
            if not is_weekend:
                st.caption("Weekly summary available on Friday/Saturday")

        # Daily Summary
        st.markdown('<div class="section-header">📋 Daily Summary</div>', unsafe_allow_html=True)
        if st.session_state.daily_summary:
            st.markdown(f'<div class="analysis-card"><span class="badge-daily">📅 Today</span><br>{st.session_state.daily_summary}</div>', unsafe_allow_html=True)
        else:
            st.info("Click 'Refresh Daily Summary' above or add transactions — it will update automatically")

        # Weekly Summary (only on Friday/Saturday)
        if is_weekend:
            st.markdown('<div class="section-header">📅 Weekly Summary</div>', unsafe_allow_html=True)
            if st.session_state.weekly_summary:
                st.markdown(f'<div class="analysis-card"><span class="badge-weekly">📅 This Week</span><br>{st.session_state.weekly_summary}</div>', unsafe_allow_html=True)
            else:
                st.info("Click 'Get Weekly Summary' above")

        # Restock Alerts
        st.markdown('<div class="section-header">⚠️ Restock Alerts</div>', unsafe_allow_html=True)
        stock_levels = get_stock_levels()
        if stock_levels:
            empty = [(p, q) for p, q in stock_levels.items() if q <= 0]
            low = [(p, q) for p, q in stock_levels.items() if 0 < q < 5]
            ok = [(p, q) for p, q in stock_levels.items() if q >= 5]

            for p, q in empty:
                st.markdown(f'<div class="alert-danger">🔴 <strong>{p}</strong> — Stock finished! Reorder immediately.</div>', unsafe_allow_html=True)
            for p, q in low:
                st.markdown(f'<div class="alert-warning">🟡 <strong>{p}</strong> — Only {q} left. Refill soon.</div>', unsafe_allow_html=True)
            for p, q in ok:
                st.markdown(f'<div class="alert-success">🟢 <strong>{p}</strong> — Stock OK ({q} units)</div>', unsafe_allow_html=True)
        else:
            st.info("No stock data yet")

        # Top Products Chart
        st.markdown('<div class="section-header">🏆 Top Selling Products</div>', unsafe_allow_html=True)
        sales_by_product = {}
        for t in st.session_state.transactions:
            if t['type'] == 'sale':
                p = t['product']
                sales_by_product[p] = sales_by_product.get(p, 0) + t['total']
        if sales_by_product:
            import pandas as pd
            df = pd.DataFrame(list(sales_by_product.items()), columns=['Product', 'Revenue (₹)'])
            df = df.sort_values('Revenue (₹)', ascending=False)
            st.bar_chart(df.set_index('Product'))
            st.bar_chart(df.set_index('Product'))
            if supabase:
                try:
                    response = supabase.table("users").select("*").execute()
                    if hasattr(response, "data"):
                        st.write(response.data)
                    else:
                        st.write(response)
                except Exception as e:
                    st.error(f"Supabase query failed: {e}")
            else:
                st.info("Supabase not configured. Set SUPABASE_URL and SUPABASE_KEY in Streamlit secrets or environment.")
