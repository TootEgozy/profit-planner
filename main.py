from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_core.runnables.graph import MermaidDrawMethod
import webbrowser

class Unit(TypedDict):
    name: str
    price: float
    price_with_vat: float
    parts: List["Unit"]

class ProjectState(TypedDict):
    profession: str
    participants_count: int
    pricing_offer: float
    parts: List[Unit]
    prep_time: float
    travel_time: float
    in_event_time: float
    after_event_time: float

class InputState(TypedDict):
    string_value: str
    numeric_value: int

def modify_state(input_state: InputState) -> InputState:
    input_state['string_value'] += "!"
    input_state['numeric_value'] += 1
    print(f"modify_state executed: {input_state}")
    return input_state

graph = StateGraph(InputState)

graph.add_node("branch_a", modify_state)
graph.add_node("branch_b", modify_state)
graph.add_edge("branch_a", "branch_b")
graph.add_edge("branch_b", END)

graph.set_entry_point("branch_a")

runnable = graph.compile()

# --------------- save to png -----------------
png_bytes = runnable.get_graph().draw_mermaid_png(draw_method=MermaidDrawMethod.API)

with open("graph.png", "wb") as f:
    f.write(png_bytes)

webbrowser.open("graph.png")
