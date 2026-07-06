from dotenv import load_dotenv
load_dotenv()

import json
from typing import Annotated, TypedDict
from rich.console import Console; from rich.panel import Panel; from rich.prompt import Prompt
from langgraph.graph import StateGraph, END, START, add_messages; from langgraph.types import Send
from agents.orchestrator import run_orchestrator; from agents.spec_parser import run_spec_parser; from agents.web_search import run_web_search
from agents.price_tracker import run_price_tracker; from agents.review_analyst import run_review_analyst; from agents.deal_scorer import run_deal_scorer; from agents.synthesizer import run_synthesizer
from tools.sqlite_tool import init_db, set_alert

console = Console()

class DealSenseState(TypedDict):
    messages: Annotated[list, add_messages]; raw_query: str; clarifications_needed: bool
    clarification_questions: list[str]; structured_spec: dict; search_query: str; search_results: list
    review_results: list; triggered_alerts: list; clarification_round: int; ranked_deals: list
    final_deals: list; current_step: str; must_have_features: list; nice_to_have_features: list

def get_user_input(state: DealSenseState) -> dict:
    """Print clarification questions, collect user response, and update state."""
    questions = state.get("clarification_questions", [])
    console.print(Panel("\n".join(questions), style="yellow", title="Clarification Questions"))
    user_input = Prompt.ask("Your response")
    console.print(Panel(user_input, style="green", title="User Input"))
    return {
        "messages": [("user", user_input)], "raw_query": f"{state['raw_query']}\nUser clarification: {user_input}",
        "clarification_round": state.get("clarification_round", 0) + 1, "current_step": "get_user_input"
    }

def route_after_orchestrator(state: DealSenseState) -> str:
    """Route based on clarification needs."""
    return "get_user_input" if state.get("clarifications_needed", False) else "spec_parser"

def route_after_web_search(state: DealSenseState) -> list[Send]:
    """Route to price_tracker and review_analyst in parallel."""
    return [Send("price_tracker", state), Send("review_analyst", state)]

def build_graph() -> StateGraph:
    """Build and compile the DealSense StateGraph."""
    w = StateGraph(DealSenseState)
    for n, o in [("orchestrator", run_orchestrator), ("get_user_input", get_user_input), ("spec_parser", run_spec_parser), ("web_search", run_web_search), ("price_tracker", run_price_tracker), ("review_analyst", run_review_analyst), ("deal_scorer", run_deal_scorer), ("synthesizer", run_synthesizer)]: w.add_node(n, o)
    for s, d in [(START, "orchestrator"), ("get_user_input", "orchestrator"), ("spec_parser", "web_search"), ("price_tracker", "deal_scorer"), ("review_analyst", "deal_scorer"), ("deal_scorer", "synthesizer"), ("synthesizer", END)]: w.add_edge(s, d)
    w.add_conditional_edges("orchestrator", route_after_orchestrator, {"get_user_input": "get_user_input", "spec_parser": "spec_parser"})
    w.add_conditional_edges("web_search", route_after_web_search, ["price_tracker", "review_analyst"])
    return w.compile()

graph = build_graph()

def run_dealsense(query: str) -> dict:
    """Run full DealSense pipeline and return final state."""
    initial_state = {
        "messages": [], "raw_query": query, "clarifications_needed": False,
        "clarification_questions": [], "structured_spec": {}, "search_query": "",
        "search_results": [], "review_results": [], "ranked_deals": [],
        "final_deals": [], "triggered_alerts": [], "current_step": "", "clarification_round": 1,
        "must_have_features": [], "nice_to_have_features": []
    }
    return graph.invoke(initial_state)

def main() -> None:
    """Run the interactive CLI loop for product search."""
    init_db()
    try: set_alert("Anker", 50.0)
    except Exception: pass
    query = Prompt.ask("Enter initial product search query")
    state = {
        "messages": [("user", query)], "raw_query": query,
        "clarifications_needed": False, "clarification_questions": [],
        "structured_spec": {}, "search_query": "", "search_results": [],
        "review_results": [], "triggered_alerts": [], "clarification_round": 0,
        "ranked_deals": [], "final_deals": [], "current_step": "start",
        "must_have_features": [], "nice_to_have_features": []
    }
    res = graph.invoke(state)
    console.print(Panel(json.dumps(res.get("structured_spec", {}), indent=2), style="cyan", title="Final Structured Spec"))

if __name__ == "__main__":
    main()
