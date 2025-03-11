import os
from typing import Annotated

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

from prompt import MAIN_PROMPT_TEMPLATE

load_dotenv()

llm = ChatAnthropic(model_name="claude-3-5-haiku-latest", api_key=os.environ.get("ANTHROPIC_API_KEY"))

class FlightBookingState(TypedDict):
    messages: Annotated[list, add_messages]

def chatbot(state: FlightBookingState) -> FlightBookingState:
    base_prompt = MAIN_PROMPT_TEMPLATE.format(messages=state["messages"])
    return {"messages": [llm.invoke(base_prompt)]}

graph_builder = StateGraph(FlightBookingState)
graph_builder.add_node("chatbot", chatbot)
graph_builder.set_entry_point("chatbot")
graph_builder.set_finish_point("chatbot")
memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)

def stream_graph_updates(messages: str, session: str):
    for event in graph.stream({"messages": [{"role": "user", "content": messages}]},
    {"configurable": {"thread_id": session}},
    ):
        for value in event.values():
            value["messages"][-1].pretty_print()
            return value["messages"][-1].content