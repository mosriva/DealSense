from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from rich.console import Console
from rich.panel import Panel

console = Console()

def match_review(product_name: str, review_results: list) -> dict:
    """Find a review matching the product name by checking if product name contains review product name words."""
    p_name_lower = product_name.lower()
    for r in review_results:
        r_name = r.get("product_name", "")
        if not r_name: continue
        r_words = {w.strip(".,!-()\"'").lower() for w in r_name.split() if len(w) > 2}
        r_words = {w for w in r_words if w and w not in {"buy", "this", "product", "review"}}
        if r_words and all(w in p_name_lower for w in r_words):
            return r
    return {}

def generate_why(rank: int, spec: dict, p: dict, rev: dict) -> str:
    """Generate a one-sentence explanation of why the product was ranked."""
    use_case = spec.get("use_case") or "general use"
    budget = spec.get("budget_max") or 50.0
    pros = ", ".join(rev.get("pros", ["No pros listed"]))
    prompt = f"In one sentence explain why this product is ranked #{rank} for someone looking for {use_case} with budget ${budget}: {p.get('name')} at {p.get('price')} with score {p.get('deal_score', 0.0) * 10}/10 and these pros: {pros}"
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.0, max_retries=0)
        res = llm.invoke([SystemMessage(content="You are a product search assistant. Answer in one sentence."), HumanMessage(content=prompt)])
        return res.content.strip()
    except Exception:
        return f"Ranked #{rank} because it matches the category and features requested within budget."

def run_synthesizer(state: dict) -> dict:
    """Synthesize final ranked deals with explanations and print formatted results."""
    ranked = state.get("ranked_deals", [])
    reviews = state.get("review_results", [])
    spec = state.get("structured_spec", {})
    
    final_deals = []
    colors = {1: "gold3", 2: "grey78", 3: "dark_orange3"}
    
    for p in ranked[:3]:
        rev = match_review(p.get("name", ""), reviews)
        why = generate_why(p["rank"], spec, p, rev)
        
        deal = {
            "rank": p["rank"],
            "name": p.get("name", ""),
            "price": p.get("price", "Check site for price"),
            "url": p.get("url", ""),
            "source": p.get("source", ""),
            "deal_score": p.get("deal_score", 0.0),
            "community_score": rev.get("community_score", 5.0),
            "pros": rev.get("pros", []),
            "cons": rev.get("cons", []),
            "why": why,
            "alert_set": False
        }
        final_deals.append(deal)
        
        border = colors.get(deal["rank"], "white")
        info = f"Rank: {deal['rank']}\nName: {deal['name']}\nPrice: {deal['price']}\nSource: {deal['source']}\nScore: {deal['deal_score']}/1.0\nCommunity Score: {deal['community_score']}/10.0\nPros: {', '.join(deal['pros'])}\nCons: {', '.join(deal['cons'])}\nWhy: {deal['why']}"
        console.print(Panel(info, border_style=border, title=f"Deal Rank #{deal['rank']}"))
        
    return {"final_deals": final_deals, "current_step": "synthesizer"}
