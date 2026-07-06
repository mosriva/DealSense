import re
from rich.console import Console
from rich.panel import Panel

console = Console()

def parse_price(price_str: str) -> float:
    """Parse price string to float, returning None on failure."""
    if not price_str or "check site" in price_str.lower():
        return None
    try:
        cleaned = re.sub(r"[^\d.]", "", price_str)
        return float(cleaned) if cleaned else None
    except Exception:
        return None

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

def run_deal_scorer(state: dict) -> dict:
    """Compute deal scores, rank products, and print scored products."""
    products = state.get("search_results", [])
    reviews = state.get("review_results", [])
    spec = state.get("structured_spec", {})
    budget = float(spec.get("budget_max") or 50.0)
    req_features = spec.get("features", [])
    
    scored = []
    for p in products:
        price_val = parse_price(p.get("price"))
        price_score = 1.0 - (price_val / budget) if price_val is not None else 0.5
        
        desc = p.get("description", "").lower()
        matched_feats = sum(1 for f in req_features if f.lower() in desc)
        spec_score = (matched_feats / len(req_features)) if req_features else 1.0
        
        rev = match_review(p.get("name", ""), reviews)
        score_val = rev.get("community_score")
        try:
            review_score = float(score_val) / 10.0 if score_val is not None else 0.5
        except Exception:
            review_score = 0.5
            
        deal_score = round((price_score * 0.35) + (spec_score * 0.35) + (review_score * 0.30), 2)
        
        p_copy = dict(p)
        p_copy["deal_score"] = deal_score
        scored.append(p_copy)
        
    scored.sort(key=lambda x: x["deal_score"], reverse=True)
    
    for i, p in enumerate(scored):
        p["rank"] = i + 1
        console.print(Panel(
            f"Name: {p.get('name')}\nPrice: {p.get('price')}\nScore: {p.get('deal_score')}/1.0",
            style="cyan",
            title=f"Rank #{p['rank']}"
        ))
        
    return {"ranked_deals": scored, "current_step": "deal_scorer"}
