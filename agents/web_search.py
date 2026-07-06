import json, os
from dotenv import load_dotenv
from rich.console import Console; from rich.panel import Panel
from tools.search_tool import serpapi_search, serpapi_shopping_search
from agents.web_search_helper import is_valid_product_url, parse_results_with_gemini

load_dotenv()
console = Console()

def filter_relevant_results(results: list, spec: dict) -> list:
    """Use Gemini to filter results keeping only those relevant to the search spec."""
    if not results: return results
    from langchain_google_genai import ChatGoogleGenerativeAI
    import json, re; llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    category = spec.get("category", "")
    features = spec.get("must_have_features", []) + spec.get("nice_to_have_features", [])
    products_summary = "\n".join([f"{i+1}. {r.get('name', '')} — {r.get('description', '')[:100]}" for i, r in enumerate(results)])
    prompt = f'You are a product relevance filter.\nCategory requested: {category}\nFeatures requested: {features}\n\nProducts found:\n{products_summary}\n\nReturn ONLY a JSON array of the index numbers (1-based) of products that are ACTUALLY in the category "{category}".\nReject anything that is clearly a different product category.\nExample: if category is "electric scooter" reject butter dishes, memberships, accessories.\nReturn format: [1, 3, 5] — only the numbers of relevant products.'
    try:
        match = re.search(r'\[.*?\]', llm.invoke(prompt).content.strip(), re.DOTALL)
        if match:
            indices = json.loads(match.group())
            filtered = [results[i-1] for i in indices if 0 < i <= len(results)]
            if filtered: return filtered
    except: pass
    return results

def run_web_search(state: dict) -> dict:
    """Search for products and extract structured info."""
    console.print(Panel("Searching for products...", style="blue", title="Web Search"))
    spec = state.get("structured_spec", {})
    cat = spec.get("category", "product")
    budget = spec.get("budget_max")
    features = " ".join(spec.get("must_have_features", []) + spec.get("nice_to_have_features", []))
    q = f'"{cat}" specific product buy best under ${budget or 50} {features} site:amazon.com OR site:bestbuy.com OR site:walmart.com'
    raw = serpapi_search(q, count=8)
    valid = [r for r in raw if is_valid_product_url(r.get("url"))]
    if len(valid) < 5:
        q2 = f'"{cat}" buy {features} under ${budget or 50} -site:reddit.com'
        for r in serpapi_search(q2, count=8):
            if is_valid_product_url(r.get("url")) and r.get("url") not in {v.get("url") for v in valid}:
                valid.append(r)
    products = parse_results_with_gemini(valid)
    filtered = filter_relevant_results(products, spec)
    for p in filtered[:3]:
        pname = p.get("name", "")
        if not pname: continue
        w1 = {w.lower() for w in pname.split() if len(w) > 2}
        shop = serpapi_shopping_search(f"{pname} {budget or ''}".strip(), count=3)
        for s in shop:
            w2 = {w.lower() for w in s.get("title", "").split() if len(w) > 2}
            if w1 & w2 and s.get("price"):
                p["price"] = s["price"]
                break
    for p in filtered:
        p["price"] = p.get("price") or "Check site for price"
        console.print(Panel(f"Name: {p.get('name')}\nPrice: {p.get('price')}\nURL: {p.get('url')}", style="green", title="Found Product"))
    return {"search_results": filtered, "current_step": "web_search"}
