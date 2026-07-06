from rich.console import Console
from rich.panel import Panel

def run_spec_parser(state: dict) -> dict:
    """Build an optimized search query string from the structured specifications."""
    Console().print(Panel("Building search query...", style="blue", title="Spec Parser"))
    spec = state.get("structured_spec", {})
    category = spec.get("category", "")
    budget = spec.get("budget_max")
    must_have = spec.get("must_have_features", [])
    
    query_parts = [f'"{category}"'] if category else []
    if must_have:
        query_parts.extend(must_have)
    if budget:
        query_parts.append(f"under ${budget}")
    query_parts.append("buy")
    query_parts.append("site:amazon.com OR site:bestbuy.com OR site:walmart.com")
    
    return {
        "search_query": " ".join(query_parts),
        "current_step": "spec_parser"
    }
