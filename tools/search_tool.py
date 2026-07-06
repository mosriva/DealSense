import os
from urllib.parse import urlparse
from dotenv import load_dotenv
from serpapi import GoogleSearch

load_dotenv()

def serpapi_search(query: str, count: int = 5, tbm: str = None) -> list[dict]:
    """Search Google via SerpAPI, return list of {title, url, snippet, source, price}."""
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        return []
    try:
        params = {"q": query, "api_key": api_key, "num": count}
        if tbm:
            params["tbm"] = tbm
        results = GoogleSearch(params).get_dict()
        items = results.get("shopping_results") or results.get("organic_results", [])
        res = []
        for item in items:
            url = item.get("link") or ""
            source = urlparse(url).netloc.replace("www.", "") if url else ""
            price = item.get("price") or item.get("extracted_price") or ""
            res.append({
                "title": item.get("title") or "",
                "url": url,
                "snippet": item.get("snippet") or "",
                "source": source,
                "price": price
            })
        return res
    except Exception:
        return []

def serpapi_shopping_search(query: str, count: int = 3) -> list[dict]:
    """Search Google Shopping via SerpAPI, return list of {title, price, link, source}."""
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        return []
    try:
        params = {"engine": "google_shopping", "q": query, "api_key": api_key, "num": count}
        results = GoogleSearch(params).get_dict()
        res = []
        for item in results.get("shopping_results", []):
            url = item.get("link") or ""
            source = urlparse(url).netloc.replace("www.", "") if url else ""
            res.append({
                "title": item.get("title") or "",
                "price": item.get("price") or "",
                "url": url,
                "source": source
            })
        return res
    except Exception:
        return []
