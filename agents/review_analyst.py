import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from rich.console import Console; from rich.panel import Panel
from tools.search_tool import serpapi_search

load_dotenv()
console = Console()

SYSTEM_PROMPT = """Analyze user reviews and extract details.
Return ONLY JSON: {"community_score": number, "pros": [str, str, str], "cons": [str, str, str], "review_consensus": str}"""

def extract_specific_product_name(description: str) -> str:
    """Use Gemini to extract the specific product name from a description."""
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.0, max_retries=0)
    p = "Extract specific product name from description. Return ONLY the name."
    try:
        res = llm.invoke([SystemMessage(content=p), HumanMessage(content=description)])
        return res.content.strip()
    except Exception:
        return " ".join(description.split()[:5])

def analyze_reviews(product_name: str, snippets: list) -> dict:
    """Use Gemini to extract score, pros, cons, and consensus from review snippets."""
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.0, max_retries=0)
    messages = [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=f"Snippets for {product_name}:\n{json.dumps(snippets, indent=2)}")]
    try:
        res = llm.invoke(messages, response_format={"type": "json_object"})
        content = res.content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1].rsplit("\n", 1)[0].strip()
            if content.startswith("json"): content = content[4:].strip()
        data = json.loads(content)
        if float(data.get("community_score", 0.0)) == 0.0: raise ValueError()
        data["product_name"] = product_name
        return data
    except Exception:
        prompt = f"Rate this product 1-10 based on these reviews and list 2 pros and 2 cons: {json.dumps(snippets, indent=2)}"
        try:
            res = llm.invoke([SystemMessage(content="Return ONLY JSON: {\"community_score\": float, \"pros\": [str, str], \"cons\": [str, str], \"review_consensus\": str}"), HumanMessage(content=prompt)], response_format={"type": "json_object"})
            content = res.content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1].rsplit("\n", 1)[0].strip()
                if content.startswith("json"): content = content[4:].strip()
            data = json.loads(content)
            data["product_name"] = product_name
            return data
        except Exception:
            return {"product_name": product_name, "community_score": 0.0, "pros": ["No pros"], "cons": ["No cons"], "review_consensus": "Error analyzing reviews."}

def run_review_analyst(state: dict) -> dict:
    """Review analyst node to search user reviews and summarize them with Gemini."""
    products = state.get("search_results", [])[:3]
    results = []
    for p in products:
        name = p.get("name", "")
        desc = p.get("description", "")
        specific_name = extract_specific_product_name(desc) if desc else name
        q = f"{specific_name} review pros cons 2024 site:rtings.com OR site:tomsguide.com OR site:reddit.com"
        raw = serpapi_search(q, count=5)
        snippets = [r.get("snippet", "") for r in raw]
        analysis = analyze_reviews(specific_name, snippets)
        results.append(analysis)
        info = f"Product: {specific_name}\nScore: {analysis.get('community_score')}/10\nPros: {', '.join(analysis.get('pros', []))}\nCons: {', '.join(analysis.get('cons', []))}\nConsensus: {analysis.get('review_consensus')}"
        console.print(Panel(info, style="magenta", title="Review Analysis"))
    return {"review_results": results}
