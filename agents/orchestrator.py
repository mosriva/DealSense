import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from rich.console import Console; from rich.panel import Panel; from rich.prompt import Prompt

SYSTEM_PROMPT = """You are a product search assistant. Extract structured specs from the user query.
IMPORTANT: Always identify the product category from the query — this is the most important field.

Return ONLY valid JSON with these exact keys:
{
  "category": "<specific product type e.g. electric scooter, laptop, power bank>",
  "budget_max": <number or null>,
  "must_have_features": ["feature1", "feature2"],
  "nice_to_have_features": ["feature1", "feature2"],
  "brand_preference": "<brand or null>",
  "use_case": "<who is it for or what for, e.g. 12 year old girl, video editing>"
}

Examples:
Query: "find electric scooter for 12 year old girl"
→ {"category": "electric scooter", "budget_max": null, "must_have_features": ["safe for kids", "age appropriate"], "nice_to_have_features": ["lightweight", "adjustable speed"], "brand_preference": null, "use_case": "12 year old girl"}

Query: "find laptop for programming under $1200"
→ {"category": "laptop", "budget_max": 1200, "must_have_features": ["programming"], "nice_to_have_features": ["lightweight", "long battery"], "brand_preference": null, "use_case": "programming"}

Return ONLY the JSON object. No other text."""

def call_gemini(query: str) -> dict:
    """Call Gemini to analyze the query and return the parsed JSON response."""
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.0, max_retries=0)
    messages = [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=f"Query: {query}")]
    try: res = llm.invoke(messages, response_format={"type": "json_object"})
    except Exception as e:
        Console().print(Panel(f"Gemini Error: {str(e)}", style="red", title="Gemini Invoke Failure"))
        raise e
    content = res.content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[1].rsplit("\n", 1)[0].strip()
        if content.startswith("json"): content = content[4:].strip()
    return json.loads(content)

def run_orchestrator(state: dict) -> dict:
    """Orchestrator node that checks if clarification is needed or extracts specifications."""
    console = Console(); console.print(Panel("Orchestrator thinking...", style="blue", title="Orchestrator"))
    raw_query = state.get("raw_query", "")
    try: data = call_gemini(raw_query)
    except Exception:
        console.print("[yellow]Gemini failed. Asking for query retype...[/]")
        raw_query = Prompt.ask("Please retype your product search query once")
        try: data = call_gemini(raw_query)
        except Exception:
            console.print("[yellow]Gemini retry failed. Proceeding with default spec.[/]")
            data = {"category": "power bank" if "bank" in raw_query.lower() else "product", "budget_max": 50 if "50" in raw_query else None, "must_have_features": ["fast charging"] if "charging" in raw_query else [], "nice_to_have_features": [], "brand_preference": None, "use_case": None}
    spec = data.get("structured_spec") or data or {}
    if not spec.get("category") or str(spec["category"]).lower() in ["null", "none", ""]:
        spec["category"] = "power bank" if "bank" in raw_query.lower() else "product"
    spec["features"] = spec.get("must_have_features", []) + spec.get("nice_to_have_features", [])
    return {"clarifications_needed": False, "clarification_questions": [], "structured_spec": spec, "raw_query": raw_query, "current_step": "orchestrator"}
