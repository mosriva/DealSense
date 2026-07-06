import sqlite3, re, streamlit as st

DB = "data/dealsense.db"
STEP_MAP = {
    "orchestrator": "🧠 Orchestrator — Analyzing your request", "spec_parser": "📋 Spec Parser — Building search query",
    "web_search": "🔍 Web Search — Finding products", "review_analyst": "⭐ Review Analyst — Analyzing reviews",
    "price_tracker": "💰 Price Tracker — Tracking prices", "deal_scorer": "🏆 Deal Scorer — Ranking deals",
    "synthesizer": "✨ Synthesizer — Generating recommendations"
}
CSS_STYLE = "<style>[data-testid='metric-container'] { background-color: rgba(28, 131, 98, 0.1); border: 1px solid rgba(28, 131, 98, 0.3); border-radius: 8px; padding: 10px; } [data-testid='stMetricValue'] { color: #1D9E75; font-size: 24px; font-weight: bold; } [data-testid='stMetricLabel'] { color: var(--text-color); font-size: 12px; } div[data-testid='stExpander'] { border: 1px solid #2d3748; border-radius: 8px; } .stAlert { border-radius: 8px; }</style>"

def get_active_alerts() -> list:
    """Get active price alerts from sqlite."""
    try:
        with sqlite3.connect(DB) as conn: return conn.execute("SELECT product_name, threshold_price FROM alerts WHERE active = 1").fetchall()
    except Exception: return []

def get_searches_today() -> int:
    """Get count of searches today from price_history."""
    try:
        with sqlite3.connect(DB) as conn: return conn.execute("SELECT COUNT(*) FROM price_history WHERE date(timestamp) = date('now')").fetchone()[0]
    except Exception: return 0

def parse_price(price_str: str) -> float:
    """Parse price string to float."""
    if not price_str or "check" in price_str.lower(): return None
    try: return float(re.sub(r"[^\d.]", "", price_str))
    except Exception: return None

def parse_list_field(field) -> list:
    """Parse pros/cons field whether it arrives as list, string, or None."""
    if not field: return []
    if isinstance(field, list): return [str(i).strip() for i in field if i]
    if isinstance(field, str):
        for delim in ["\n", ".,", ",", ";"]:
            parts = [p.strip() for p in field.split(delim) if p.strip()]
            if len(parts) > 1: return parts
        return [field.strip()] if field.strip() else []
    return []

def get_pros_cons(deal: dict, review_results: list) -> tuple[list, list]:
    """Get pros and cons from deal dict or matching review result."""
    pros = parse_list_field(deal.get("pros") or deal.get("Pros") or deal.get("advantages"))
    cons = parse_list_field(deal.get("cons") or deal.get("Cons") or deal.get("disadvantages"))
    if not pros and not cons and review_results:
        deal_name = deal.get("name", "").lower()
        for review in review_results:
            review_name = review.get("product_name", "").lower()
            deal_words = set(deal_name.split())
            review_words = set(review_name.split())
            if len(deal_words & review_words) >= 2:
                pros = parse_list_field(review.get("pros"))
                cons = parse_list_field(review.get("cons"))
                break
    return pros, cons

def sidebar_stat(label: str, value: str) -> None:
    """Render a sidebar statistic box."""
    st.sidebar.markdown(f"<div style='background:rgba(28,131,98,0.1);border:1px solid rgba(28,131,98,0.3);border-radius:8px;padding:12px;margin:4px 0'><p style='margin:0;font-size:12px;color:gray'>{label}</p><p style='margin:0;font-size:24px;font-weight:bold;color:#1D9E75'>{value}</p></div>", unsafe_allow_html=True)

def render_sidebar(deals_state: dict, active_alerts: list) -> None:
    """Render the sidebar UI components."""
    st.sidebar.title("🔍 DealSense")
    st.sidebar.caption("Multi-agent AI product search")
    st.sidebar.divider()
    st.sidebar.subheader("How it works")
    st.sidebar.markdown("1. 🧠 **Orchestrator** understands query\n2. 📋 **Spec Parser** builds specs\n3. 🔍 **Web Search** finds products\n4. ⭐ **Review Analyst** reads reviews\n5. 💰 **Price Tracker** monitors prices\n6. 🏆 **Deal Scorer** ranks by value\n7. ✨ **Synthesizer** recommends")
    st.sidebar.divider()
    st.sidebar.subheader("📊 Session Stats")
    sidebar_stat("Searches Today", str(get_searches_today()))
    sidebar_stat("Products Found This Session", str(len(deals_state.get("search_results", [])) if deals_state else 0))
    sidebar_stat("Active Alerts", str(len(active_alerts)))
    st.sidebar.divider()
    st.sidebar.subheader("🔔 Price Alerts")
    for name, thresh in active_alerts: st.sidebar.write(f"🔔 {name}: ${thresh:.2f}")
    triggered = deals_state.get("triggered_alerts", []) if deals_state else []
    for a in triggered:
        st.sidebar.error(f"🚨 ALERT TRIGGERED!\n{a['product_name']} is ${a['current_price']} (Threshold: ${a['threshold_price']})")
