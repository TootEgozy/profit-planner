from typing import TypedDict, List, NotRequired
from langgraph.graph import StateGraph, END
from langchain_core.runnables.graph import MermaidDrawMethod
import pandas as pd
import webbrowser
import re

class Unit(TypedDict):
    name: str
    price: float
    price_with_vat: float
    parts: List["Unit"]
    amount_needed: int
    amount_in_packet: int
    packet_price: float
    packet_price_with_vat: float

class ProjectState(TypedDict):
    profession: str
    event_type: str
    participants_count: int
    pricing_offer: float
    parts: List[Unit]
    prep_time: float
    travel_time: float
    in_event_time: float
    after_event_time: float

class InputState(TypedDict):
    string_value: NotRequired[str]
    numeric_value: NotRequired[int]

initial_state: ProjectState = {
    "profession": "",
    "event_type": "",
    "participants_count": 0,
    "pricing_offer": 0.0,
    "parts": [],
    "prep_time": 0.0,
    "travel_time": 0.0,
    "in_event_time": 0.0,
    "after_event_time": 0.0,
}

# ------------------------- nodes -----------------------
def modify_state(input_state: InputState) -> InputState:
    return input_state


def collect_basic_info(state: ProjectState) -> ProjectState:
    state["profession"] = input("Enter your profession: ").strip()
    state["event_type"] = input("Which type of event are you working on?: ").strip()
    state["participants_count"] = int(
        input("Number of participants: ").strip()
    )

    return state

def load_price_catalog(path: str) -> dict:
    df = pd.read_excel(path)

    catalog = {}
    for _, row in df.iterrows():
        catalog[row["name"]] = {
            "unit_type": row["unit_type"],
            "price": float(row["price"]),
            "price_with_vat": float(row["price_with_vat"]),
            "packet_size": int(row["packet_size"]),
            "packet_price": float(row["packet_price"]),
            "packet_price_with_vat": float(row["packet_price_with_vat"]),
        }
    return catalog


def collect_top_level_units() -> list[Unit]:
    print("What are you making or buying for this event?")
    print("Examples: Table arrangement, Bridal bouquet, Arch, Reception flowers")
    
    units = [Unit]

    prodcuts = re.split(r'[, ]+', input("Enter all product names seperated by a comma/n").strip())

    for p in prodcuts:
        unit = {
            "amount_needed": int(input(f"How many {p}s? ").strip()),
            "parts": [],
        }

        is_purchased = bool(input(f"Are you buying {p}?"))
        if is_purchased:
            unit['price'] = float(input("Price without tax: "))
            unit['price_with_vat'] = float(input("Price without tax: "))
            unit['amount_in_packet'] = int(input("How much in packet: "))
            unit['packet_price'] = float(input("Packet price (no vat): "))
            unit['packet_price_with_vat'] = float(input("Packet price including vat: "))
        
        units.append(unit)

    return units
# ---------------------- graph --------------------------

graph = StateGraph(ProjectState)

graph.add_node("collect_basic_info", collect_basic_info)
graph.set_entry_point("collect_basic_info")
graph.add_edge("collect_basic_info", END)

runnable = graph.compile()

# ---------------------- run ---------------------------

final_state = runnable.invoke(initial_state)
print("\nFinal state:")
print(final_state)


# --------------- save to png -----------------
png_bytes = runnable.get_graph().draw_mermaid_png(draw_method=MermaidDrawMethod.API)

with open("graph.png", "wb") as f:
    f.write(png_bytes)

webbrowser.open("graph.png")
