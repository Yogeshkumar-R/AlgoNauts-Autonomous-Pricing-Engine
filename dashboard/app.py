"""
AlgoNauts Autonomous Pricing Engine - Demo Dashboard
"""

import streamlit as st
import requests
import json
import os
import time
from datetime import datetime
from dotenv import load_dotenv,find_dotenv

load_dotenv(find_dotenv())

API_BASE = os.getenv("API_BASE")

# ─────────────────────────── CONFIG ──────────────────────────────────────────

PRODUCTS = {
    "PROD-001": "🎧 Wireless Bluetooth Earbuds",
    "PROD-002": "💧 Stainless Steel Water Bottle",
    "PROD-003": "🔌 USB-C Fast Charging Cable",
    "PROD-004": "🧘 Yoga Mat Premium",
    "PROD-005": "💡 LED Desk Lamp",
}

EVENT_TYPES = {
    "random": "🎲 Random Scenario",
    "competitor_drop": "📉 Competitor Price Drop",
    "demand_spike": "🔥 Demand Surge",
    "inventory_shift": "📦 Inventory Shift",
}

st.set_page_config(
    page_title="AlgoNauts — Autonomous Pricing Engine",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────── CUSTOM CSS ──────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.main { background: #0a0e1a; }

/* Hero */
.hero {
    background: linear-gradient(135deg, #1a1f35 0%, #0d1224 50%, #0a0e1a 100%);
    border: 1px solid rgba(99, 102, 241, 0.3);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -20%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(99,102,241,0.15) 0%, transparent 70%);
    border-radius: 50%;
}
.hero h1 {
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #a78bfa, #60a5fa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 0.25rem 0;
}
.hero p { color: #94a3b8; margin: 0; font-size: 1rem; }

/* Metric cards */
.metric-card {
    background: linear-gradient(135deg, #1e2440, #161c30);
    border: 1px solid rgba(99,102,241,0.25);
    border-radius: 12px;
    padding: 1.25rem;
    text-align: center;
    transition: border-color 0.2s;
}
.metric-card:hover { border-color: rgba(99,102,241,0.6); }
.metric-value {
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #a78bfa, #60a5fa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.metric-label { color: #64748b; font-size: 0.8rem; margin-top: 0.25rem; }

/* Status pill */
.pill-success { background: #052e16; color: #4ade80; border: 1px solid #166534; border-radius: 999px; padding: 2px 12px; font-size: 0.8rem; }
.pill-error   { background: #450a0a; color: #f87171; border: 1px solid #7f1d1d; border-radius: 999px; padding: 2px 12px; font-size: 0.8rem; }
.pill-running { background: #0c1a4b; color: #60a5fa; border: 1px solid #1d4ed8; border-radius: 999px; padding: 2px 12px; font-size: 0.8rem; }

/* Pipeline steps */
.step-done    { background: #052e16; border: 1px solid #166534; border-radius: 10px; padding: 0.75rem 1rem; margin: 0.4rem 0; }
.step-active  { background: #0c1a4b; border: 1px solid #3b82f6; border-radius: 10px; padding: 0.75rem 1rem; margin: 0.4rem 0; animation: pulse 1.5s infinite; }
.step-pending { background: #1a1f35; border: 1px solid rgba(99,102,241,0.15); border-radius: 10px; padding: 0.75rem 1rem; margin: 0.4rem 0; color: #4b5563; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.7} }

/* Output box */
.output-box {
    background: #0d1117;
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 10px;
    padding: 1rem 1.25rem;
    font-family: 'Courier New', monospace;
    font-size: 0.85rem;
    color: #c9d1d9;
    max-height: 300px;
    overflow-y: auto;
}

/* AI chat bubble */
.ai-bubble {
    background: linear-gradient(135deg, #1e2440, #161c30);
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 0 12px 12px 12px;
    padding: 1rem 1.25rem;
    margin: 0.5rem 0;
    color: #e2e8f0;
    line-height: 1.6;
}
.user-bubble {
    background: rgba(99,102,241,0.15);
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 12px 0 12px 12px;
    padding: 1rem 1.25rem;
    margin: 0.5rem 0;
    color: #e2e8f0;
    text-align: right;
}

/* Link button */
.link-btn {
    display: inline-block;
    background: linear-gradient(135deg, #6366f1, #4f46e5);
    color: white !important;
    text-decoration: none !important;
    border-radius: 8px;
    padding: 0.5rem 1.25rem;
    font-size: 0.85rem;
    font-weight: 500;
    transition: opacity 0.2s;
}
.link-btn:hover { opacity: 0.85; }

/* Section header */
.section-header {
    color: #94a3b8;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin: 1.5rem 0 0.75rem 0;
    border-bottom: 1px solid rgba(99,102,241,0.15);
    padding-bottom: 0.5rem;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1224 0%, #0a0e1a 100%);
    border-right: 1px solid rgba(99,102,241,0.2);
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────── HELPERS ─────────────────────────────────────────
def api_call(method: str, path: str, payload: dict = None, timeout: int = 30):
    url = f"{API_BASE}{path}"
    try:
        if method == "POST":
            resp = requests.post(url, json=payload or {}, timeout=timeout)
        else:
            resp = requests.get(url, timeout=timeout)
        return resp.json(), resp.status_code
    except requests.exceptions.Timeout:
        return {"error": "Request timed out"}, 504
    except Exception as e:
        return {"error": str(e)}, 500

def ts():
    return datetime.now().strftime("%H:%M:%S")

# ─────────────────────────── SIDEBAR ─────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0 1.5rem 0;">
        <div style="font-size:2.5rem">🤖</div>
        <div style="font-size:1.1rem; font-weight:700; color:#a78bfa;">AlgoNauts</div>
        <div style="font-size:0.75rem; color:#4b5563;">Autonomous Pricing Engine</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        ["🚀 Demo Simulator", "💬 AI Pricing Manager", "📊 Product Catalog", "🔗 API Explorer"],
        label_visibility="collapsed",
    )

    st.markdown("<div class='section-header'>Quick Links</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>Status</div>", unsafe_allow_html=True)
    st.markdown("<span class='pill-success'>✅ API Online</span>", unsafe_allow_html=True)
    st.markdown("<span class='pill-success'>✅ LangSmith Active</span>", unsafe_allow_html=True)

# ─────────────────────────── HERO ────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🤖 Autonomous Pricing Engine</h1>
    <p>AI-powered real-time pricing decisions · Step Functions orchestration · LangSmith tracing</p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
#  PAGE: DEMO SIMULATOR
# ═══════════════════════════════════════════════════════════════════════════
if "🚀 Demo Simulator" in page:
    col1, col2 = st.columns([1, 1.4], gap="large")

    with col1:
        st.markdown("<div class='section-header'>⚙️ Configure Simulation</div>", unsafe_allow_html=True)

        # Step 1: Seed
        st.markdown("**Step 1 — Initialize Products**")
        if st.button("🌱 Seed Demo Products into DynamoDB", key="seed_btn", use_container_width=True):
            with st.spinner("Seeding products..."):
                data, code = api_call("POST", "/seed")
            if code == 200:
                st.success(f"✅ {data.get('message', 'Seeded successfully')}")
                st.json(data)
            else:
                st.error(f"❌ Error {code}: {json.dumps(data)}")

        st.markdown("---")

        # Step 2: Simulate
        st.markdown("**Step 2 — Trigger Pricing Pipeline**")
        event_type = st.selectbox(
            "Market Event Type",
            options=list(EVENT_TYPES.keys()),
            format_func=lambda k: EVENT_TYPES[k],
        )
        product_choice = st.selectbox(
            "Product",
            options=["Random"] + list(PRODUCTS.keys()),
            format_func=lambda k: "🎲 Random Product" if k == "Random" else PRODUCTS.get(k, k),
        )

        if st.button("🚀 Run Pricing Pipeline", key="sim_btn", use_container_width=True, type="primary"):
            payload = {"scenario": event_type}
            if product_choice != "Random":
                payload["product_id"] = product_choice

            with st.spinner("Triggering Step Functions pipeline..."):
                data, code = api_call("POST", "/simulate", payload)

            st.session_state["last_sim"] = {"result": data, "code": code, "time": ts()}

        # Show last run info
        if "last_sim" in st.session_state:
            sim = st.session_state["last_sim"]
            code = sim["code"]
            data = sim["result"]

            if code == 200:
                st.success(f"✅ Pipeline started at {sim['time']}")
                if "product_id" in data:
                    st.markdown(f"**Product:** {PRODUCTS.get(data.get('product_id', ''), data.get('product_id', 'N/A'))}")
                if "generated_data" in data:
                    ev = data["generated_data"]
                    c1, c2 = st.columns(2)
                    c1.metric("Competitor Price", f"₹{ev.get('competitor_price', 0):.2f}")
                    c2.metric("Demand Factor", f"{ev.get('demand_factor', 0):.2f}x")
            else:
                st.error(f"❌ Error {code}")
                st.code(json.dumps(data, indent=2))

    with col2:
        st.markdown("<div class='section-header'>📡 Pipeline Visualization</div>", unsafe_allow_html=True)

        pipeline_steps = [
            ("1", "🏪", "simulate_event", "Generate synthetic market event"),
            ("2", "📊", "market_processor", "Normalize & analyze market data"),
            ("3", "💹", "pricing_engine", "Calculate optimal price via ML"),
            ("4", "🛡️", "guardrail_executor", "Validate margin & price bounds"),
            ("5", "👁️", "monitoring_agent", "Detect pricing deviations"),
            ("6", "🔧", "correction_agent", "AI-powered Bedrock correction"),
        ]

        has_run = "last_sim" in st.session_state and st.session_state["last_sim"]["code"] == 200

        for i, (num, icon, name, desc) in enumerate(pipeline_steps):
            if has_run:
                css = "step-done"
                status = "✅"
            else:
                css = "step-pending"
                status = f"{num}"

            st.markdown(f"""
            <div class="{css}">
                <span style="font-size:1.1rem">{icon}</span>
                <strong style="color:#e2e8f0; margin-left:0.5rem">{name}</strong>
                <span style="float:right; opacity:0.8">{status}</span>
                <div style="color:#64748b; font-size:0.8rem; margin-top:0.25rem">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
#  PAGE: AI PRICING MANAGER
# ═══════════════════════════════════════════════════════════════════════════
elif "💬 AI Pricing Manager" in page:
    st.markdown("<div class='section-header'>💬 Ask the AI Pricing Manager</div>", unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    col1, col2 = st.columns([1, 2], gap="large")

    with col1:
        seller_id = st.text_input("Seller ID", value="SELLER-001")
        product_id = st.text_input("Product ID (optional)", value="PROD-001",
                                   placeholder="Leave blank for general query")

        st.markdown("**Quick Questions:**")
        quick_qs = [
            "Why did my price change?",
            "Am I priced competitively?",
            "What's my profit margin?",
            "Should I lower my price today?",
        ]
        for q in quick_qs:
            if st.button(q, key=f"q_{q}", use_container_width=True):
                st.session_state["pending_query"] = q

        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

    with col2:
        # Chat history
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f"<div class='user-bubble'>👤 {msg['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='ai-bubble'>🤖 {msg['content']}</div>", unsafe_allow_html=True)

        # Query input
        pending = st.session_state.pop("pending_query", "")
        query = st.text_area("Your question:", value=pending, height=80,
                             placeholder="e.g. Why is my product priced at ₹299?")

        if st.button("📨 Send to AI", type="primary", use_container_width=True) and query:
            st.session_state.chat_history.append({"role": "user", "content": query})

            payload = {
                "query_type": "query",
                "seller_id": seller_id,
                "query": query,
            }
            if product_id:
                payload["product_id"] = product_id

            with st.spinner("🤖 Thinking..."):
                data, code = api_call("POST", "/ai/query", payload, timeout=45)

            if code == 200:
                body = data.get("body", data)
                if isinstance(body, str):
                    body = json.loads(body)
                response = body.get("response", json.dumps(data))
            else:
                response = f"Error {code}: {json.dumps(data)}"

            st.session_state.chat_history.append({"role": "ai", "content": response})
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════
#  PAGE: PRODUCT CATALOG
# ═══════════════════════════════════════════════════════════════════════════
elif "📊 Product Catalog" in page:
    st.markdown("<div class='section-header'>📦 Product Catalog</div>", unsafe_allow_html=True)

    # Static catalog from SAMPLE_PRODUCTS
    products_data = [
        {"ID": "PROD-001", "Name": "Wireless Bluetooth Earbuds",   "Category": "Electronics",    "Cost": 450,  "Base Price": 899,  "Competitor": 849},
        {"ID": "PROD-002", "Name": "Stainless Steel Water Bottle", "Category": "Home & Kitchen", "Cost": 180,  "Base Price": 399,  "Competitor": 349},
        {"ID": "PROD-003", "Name": "USB-C Fast Charging Cable",    "Category": "Electronics",    "Cost": 95,   "Base Price": 249,  "Competitor": 199},
        {"ID": "PROD-004", "Name": "Yoga Mat Premium",             "Category": "Sports",         "Cost": 320,  "Base Price": 699,  "Competitor": 599},
        {"ID": "PROD-005", "Name": "LED Desk Lamp",                "Category": "Home & Kitchen", "Cost": 275,  "Base Price": 599,  "Competitor": 549},
    ]

    for p in products_data:
        margin = round(((p["Base Price"] - p["Cost"] * 1.18) / p["Base Price"]) * 100, 1)
        with st.expander(f"{p['ID']} — {p['Name']}", expanded=False):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("💰 Cost (incl. GST)", f"₹{p['Cost']*1.18:.0f}")
            c2.metric("🏷️ Our Price", f"₹{p['Base Price']}")
            c3.metric("🏪 Competitor", f"₹{p['Competitor']}")
            c4.metric("📈 Margin", f"{margin}%")
            st.caption(f"Category: {p['Category']} · GST: 18%")

# ═══════════════════════════════════════════════════════════════════════════
#  PAGE: API EXPLORER
# ═══════════════════════════════════════════════════════════════════════════
elif "🔗 API Explorer" in page:
    st.markdown("<div class='section-header'>🔗 Live API Explorer</div>", unsafe_allow_html=True)

    endpoints = {
        "POST /seed": {"path": "/seed", "desc": "Seed 5 demo products into DynamoDB", "payload": {}},
        "POST /simulate": {"path": "/simulate", "desc": "Trigger a full pricing pipeline run via Step Functions",
                           "payload": {"scenario": "competitor_drop", "product_id": "PROD-001"}},
        "POST /ingest/market-data": {"path": "/ingest/market-data", "desc": "Ingest real market data",
                                     "payload": {"product_id": "PROD-001", "competitor_price": 299.99, "demand_factor": 1.2}},
        "POST /ai/query": {"path": "/ai/query", "desc": "Ask the AI pricing manager",
                           "payload": {"query_type": "query", "seller_id": "SELLER-001",
                                       "query": "Should I lower my price today?", "product_id": "PROD-001"}},
    }

    selected = st.selectbox("Select Endpoint", list(endpoints.keys()))
    ep = endpoints[selected]

    st.caption(ep["desc"])
    payload_str = st.text_area("Request Body (JSON)", value=json.dumps(ep["payload"], indent=2), height=150)

    c1, c2 = st.columns([1, 5])
    with c1:
        run = st.button("▶ Send", type="primary")
    with c2:
        st.code(f"POST {API_BASE}{ep['path']}", language="bash")

    if run:
        try:
            payload = json.loads(payload_str)
        except json.JSONDecodeError:
            st.error("Invalid JSON payload")
            st.stop()

        with st.spinner(f"Calling {ep['path']}..."):
            data, code = api_call("POST", ep["path"], payload)

        if code == 200:
            st.success(f"✅ {code} OK")
        else:
            st.error(f"❌ {code}")
        st.json(data)

# ─────────────────────────── FOOTER ──────────────────────────────────────────
st.markdown("""
<div style="text-align:center; color:#374151; font-size:0.75rem; margin-top:3rem; 
            border-top:1px solid rgba(99,102,241,0.15); padding-top:1rem;">
    🤖 AlgoNauts Autonomous Pricing Engine · Built on AWS Lambda · Step Functions · Bedrock · LangSmith
</div>
""", unsafe_allow_html=True)
