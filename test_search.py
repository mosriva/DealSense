from serpapi import GoogleSearch
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("SERPAPI_KEY")
if not api_key:
    raise ValueError("SERPAPI_KEY not found in .env file")

print(f"SerpAPI key loaded: {api_key[:8]}...")
print("Searching...")

search = GoogleSearch({
    "q": "best laptop for video editing under $1000",
    "api_key": api_key,
    "num": 3
})

results = search.get_dict()
items = results.get("organic_results", [])

if not items:
    print("ERROR: No results returned")
    print(results)
else:
    print(f"\n✓ Search working — {len(items)} results returned\n")
    for item in items:
        print(f"  → {item.get('title')}")
        print(f"    {item.get('link')}")
        print(f"    {item.get('snippet', '')[:80]}...\n")

print("✓ SerpAPI connection confirmed. Ready for Day 2.")
