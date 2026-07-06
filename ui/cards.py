import urllib.parse, streamlit as st
from tools.sqlite_tool import set_alert
from ui.utils import parse_price, get_pros_cons

def render_deal_cards(deals_state: dict) -> None:
    """Render the ranked deal cards with score metrics, pros/cons, and alerts."""
    all_deals = deals_state.get("ranked_deals", []) if deals_state else []
    if not all_deals:
        all_deals = deals_state.get("final_deals", []) if deals_state else []
    if deals_state and not all_deals:
        category = (deals_state.get("structured_spec", {}) or {}).get("category") or "your search"
        st.warning(f"No relevant products found for {category}. Try broadening your search.")
        return
    all_deals = sorted(all_deals, key=lambda x: x.get("deal_score", 0), reverse=True)
    
    st.subheader(f"Top Deals Found ({len(all_deals)} results)")
    reviews = deals_state.get("review_results", []) if deals_state else []
    
    for idx, d in enumerate(all_deals):
        rank = idx + 1
        badge = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"#{rank}"
        colors = {1: "#FFD700", 2: "#C0C0C0", 3: "#CD7F32"}
        border_color = colors.get(rank, "#2d3748")
        
        with st.container(border=True):
            st.markdown(f"<div style='height:8px; background-color:{border_color}; border-radius:4px 4px 0 0;'></div>", unsafe_allow_html=True); st.markdown(f"### {badge} {d.get('name')}")
            price = d.get("price")
            if price and price != "Check site for price":
                st.markdown(f"<h2 style='color:#1D9E75;margin:0'>{price}</h2>", unsafe_allow_html=True)
            else:
                st.markdown("<p style='color:#9ca3af;font-style:italic'>Price — visit site</p>", unsafe_allow_html=True)
            c1, c2 = st.columns(2); c1.metric("Deal Score", f"{d.get('deal_score', 0.0):.0%}"); c2.metric("Community Score", f"{d.get('community_score', 0.0)}/10")
            st.info(f"💡 {d.get('why') or 'No recommendation details available.'}"); pc1, pc2 = st.columns(2)
            
            pros, cons = get_pros_cons(d, reviews)
            with pc1:
                st.markdown("**✅ Pros**")
                if pros:
                    for pro in pros[:3]: st.markdown(f"- {pro}")
                else: st.caption("No pros listed")
            with pc2:
                st.markdown("**❌ Cons**")
                if cons:
                    for con in cons[:3]: st.markdown(f"- {con}")
                else: st.caption("No cons listed")
            b1, b2 = st.columns(2)
            url = d.get("url") or f"https://www.google.com/search?tbm=shop&q={urllib.parse.quote_plus(d.get('name', ''))}"; b1.link_button("🛒 View Deal →", url, use_container_width=True)
            alert_key = f"alert_active_{rank}"
            if b2.button("🔔 Set Price Alert", key=f"btn_{rank}", use_container_width=True): st.session_state[alert_key] = True
            if st.session_state.get(alert_key):
                curr = parse_price(d.get("price")) or 50.0
                thresh = st.number_input("Threshold Price ($)", min_value=0.0, value=float(curr), key=f"val_{rank}")
                if st.button("Save Alert", key=f"save_{rank}"):
                    set_alert(d.get("name"), thresh)
                    st.success("Alert set!")
                    st.session_state[alert_key] = False
                    st.rerun()
        st.divider()
