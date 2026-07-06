import json, os, re
from urllib.parse import urlparse
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

SYSTEM_PROMPT = """Extract products from search results.
For each product, identify name, estimated price (USD or null; look for patterns like $XXX in snippets/titles), source URL, and a one-line description.
Return ONLY JSON list: [{"name": str, "price": str_or_num_or_null, "url": str, "source": str, "description": str}]"""

def is_valid_product_url(url: str) -> bool:
    """Check if URL points to a specific product page."""
    if not url: return False
    url_lower = url.lower()
    for b in ["/s?", "/searchpage", "/discover/", "/shop/pt/"]:
        if b in url_lower: return False
    try:
        segs = [s for s in urlparse(url).path.split("/") if s]
        if len(segs) < 3: return False
        last = segs[-1].lower()
        return not any(kw in last for kw in ["laptop", "battery-pack", "power-bank", "search", "category", "shop", "discover"])
    except Exception: return False

def parse_results_with_gemini(raw: list) -> list:
    """Use Gemini to extract structured product details."""
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.0, max_retries=0)
    messages = [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=f"Results:\n{json.dumps(raw, indent=2)}")]
    try:
        res = llm.invoke(messages, response_format={"type": "json_object"})
        content = res.content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1].rsplit("\n", 1)[0].strip()
            if content.startswith("json"): content = content[4:].strip()
        parsed = json.loads(content)
        if isinstance(parsed, dict):
            for v in parsed.values():
                if isinstance(v, list): return v
        return parsed if isinstance(parsed, list) else []
    except Exception:
        return [{"name": r.get("title", ""), "price": None, "url": r.get("url", ""), "source": r.get("source", ""), "description": r.get("snippet", "")} for r in raw]
