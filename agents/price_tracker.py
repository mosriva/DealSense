from rich.console import Console
from rich.panel import Panel
from tools.sqlite_tool import init_db, save_product, save_price_history, check_alerts

def run_price_tracker(state: dict) -> dict:
    """Save products, log price history, evaluate active alerts."""
    init_db()
    products = state.get("search_results", [])
    for p in products:
        name = p.get("name", "")
        url = p.get("url", "")
        price = p.get("price", "Check site for price")
        source = p.get("source", "")
        pid = save_product(name, url, price, source)
        save_price_history(pid, price)
        
    triggered = check_alerts(products)
    if triggered:
        info = "\n".join(
            f"Alert! {a['product_name']} is ${a['current_price']} (Threshold: ${a['threshold_price']})"
            for a in triggered
        )
        Console().print(Panel(info, style="red", title="Triggered Alerts"))
        
    return {"triggered_alerts": triggered}
