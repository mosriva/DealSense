import sys, os, streamlit as st; sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from main import run_dealsense
from ui.utils import get_active_alerts, render_sidebar, CSS_STYLE; from ui.cards import render_deal_cards
def check_password() -> bool:
    """Gate the entire app behind a password stored in secrets."""
    if st.session_state.get("authenticated"): return True
    st.set_page_config(page_title="DealSense", page_icon="🔍", layout="centered")
    with st.columns([1, 2, 1])[1]:
        st.markdown("## 🔍 DealSense\n##### Multi-Agent AI Product Search"); st.divider(); st.markdown("**Enter demo access password:**")
        pwd = st.text_input("", type="password", placeholder="Enter password...", label_visibility="collapsed")
        if st.button("Access Demo →", type="primary", use_container_width=True):
            if pwd == os.getenv("APP_PASSWORD", ""): st.session_state.authenticated = True; st.rerun()
            else: st.error("Incorrect password. Contact the author for access.")
        st.divider(); st.caption("🔗 [View source code](https://github.com/mosriva/DealSense)\n\nClone the repo to run with your own API keys.")
    return False
if not check_password(): st.stop()
st.set_page_config(page_title="DealSense", page_icon="🔍", layout="wide"); st.markdown(CSS_STYLE, unsafe_allow_html=True)
for k, v in [("last_query", ""), ("confirmed_budget", 50), ("confirmed_must_have", ""), ("confirmed_nice_to_have", ""), ("show_confirm", False), ("last_results", None), ("running_query", None)]: st.session_state.setdefault(k, v)
def quick_extract_specs(query: str) -> dict:
    """Extract specs from product query using Gemini."""
    from langchain_google_genai import ChatGoogleGenerativeAI
    import json, re; prompt = f'Extract from query and return ONLY valid JSON:\nQuery: "{query}"\nReturn: {{"budget": <number or null>, "category": "<product type>", "must_have": "<essential features comma separated>", "nice_to_have": "<optional features comma separated>"}}'
    try:
        match = re.search(r'\{.*\}', ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.0).invoke(prompt).content.strip(), re.DOTALL)
        if match: return json.loads(match.group())
    except: pass
    return {"budget": 50, "must_have": "", "nice_to_have": "", "category": ""}
steps = [("🧠", "Orchestrator", "Analyzing your request"), ("📋", "Spec Parser", "Building search query"), ("🔍", "Web Search", "Finding products"), ("⭐", "Review Analyst", "Analyzing reviews"), ("💰", "Price Tracker", "Tracking prices"), ("🏆", "Deal Scorer", "Ranking deals"), ("✨", "Synthesizer", "Generating recommendations")]
render_sidebar(st.session_state.last_results, get_active_alerts())
sc1, sc2, sc3 = st.columns([1, 2, 1])
with sc2:
    query = st.text_input("Product Search Query", value=st.session_state.last_query, placeholder="e.g. Find me a power bank under $50 with fast charging", label_visibility="collapsed")
    if st.button("🔍 Search Deals", use_container_width=True) and query:
        if query != st.session_state.last_query:
            st.session_state.last_query, st.session_state.last_results = query, None
            with st.spinner("Understanding your query..."): specs = quick_extract_specs(query)
            try: st.session_state.confirmed_budget = int(float(specs.get("budget") or 0))
            except: st.session_state.confirmed_budget = 0
            st.session_state.confirmed_must_have, st.session_state.confirmed_nice_to_have = str(specs.get("must_have") or ""), str(specs.get("nice_to_have") or "")
        st.session_state.show_confirm = True; st.rerun()
if st.session_state.show_confirm:
    st.markdown("**Confirm your search requirements:**"); c1, c2 = st.columns(2)
    budget = c1.number_input("💰 Max Budget ($) — leave 0 if no limit", min_value=0, max_value=50000, value=int(st.session_state.confirmed_budget or 0), step=50, key=f"budget_{st.session_state.last_query}")
    c2.caption(""); c3, c4 = st.columns(2)
    must_have = c3.text_input("✅ Must-have features", value=st.session_state.confirmed_must_have, placeholder="e.g. fast charging, waterproof", key=f"must_{st.session_state.last_query}")
    nice_to_have = c4.text_input("⭐ Nice-to-have features (optional)", value=st.session_state.confirmed_nice_to_have, placeholder="e.g. lightweight, color options", key=f"nice_{st.session_state.last_query}")
    if st.button("✅ Confirm & Search", type="primary", key=f"confirm_{st.session_state.last_query}"):
        eq = query
        if budget > 0: eq += f". Budget: under ${budget}."
        if must_have: eq += f" Must have: {must_have}."
        if nice_to_have: eq += f" Nice to have: {nice_to_have}."
        st.session_state.running_query, st.session_state.show_confirm = eq, False; st.rerun()
col1, col2 = st.columns([0.4, 0.6])
with col1:
    st.subheader("🤖 Agent Progress")
    if st.session_state.running_query:
        ph = [st.empty() for _ in steps]
        for i, (emoji, name, desc) in enumerate(steps): ph[i].markdown(f"⏳ {emoji} **{name}** — {desc}")
        ph[0].markdown(f"🔄 🧠 **Orchestrator** — Analyzing your request")
        try:
            with st.spinner("🤖 DealSense agents working..."): st.session_state.last_results = run_dealsense(st.session_state.running_query)
        except Exception as e: st.error(f"Pipeline error: {str(e)}")
        for i, (emoji, name, desc) in enumerate(steps): ph[i].markdown(f"✅ {emoji} **{name}** — {desc}")
        st.session_state.running_query = None; st.rerun()
    elif st.session_state.last_results:
        for emoji, name, desc in steps: st.markdown(f"✅ {emoji} **{name}** — {desc}")
        spec = st.session_state.last_results.get("structured_spec", {})
        must, nice = spec.get("must_have_features", []), spec.get("nice_to_have_features", [])
        with st.expander("Search Parameters", expanded=True): st.table({"Parameter": ["Category", "Budget", "Must-have", "Nice-to-have", "Use Case"], "Value": [spec.get("category", "N/A"), f"${spec.get('budget_max')}" if spec.get("budget_max") else "N/A", ", ".join(must) if must else "N/A", ", ".join(nice) if nice else "N/A", spec.get("use_case") or "N/A"]})
    else:
        for emoji, name, desc in steps: st.markdown(f"⚪ {emoji} **{name}** — {desc}")
with col2:
    if st.session_state.running_query: st.empty()
    elif st.session_state.last_results: render_deal_cards(st.session_state.last_results)
    else: st.info("Enter a product search above to find the best deals")
