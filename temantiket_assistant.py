import os
from typing import Annotated

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import START
from langgraph.graph import StateGraph, MessagesState
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

from langfuse.callback import CallbackHandler

from prompt import MAIN_PROMPT_TEMPLATE

load_dotenv()

langfuse_handler = CallbackHandler(
    public_key=os.environ.get("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.environ.get("LANGFUSE_SECRET_KEY"),
    host=os.environ.get("LANGFUSE_HOST")
)

llm = ChatAnthropic(model_name="claude-3-5-haiku-latest", api_key=os.environ.get("ANTHROPIC_API_KEY"))

prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
MAIN_PROMPT_TEMPLATE
    ),
    HumanMessagePromptTemplate.from_template(
        "Previous conversation:\n{messages}\n\nUser question: {user_input}"
    )
])

class FlightBookingState(TypedDict):
    messages: Annotated[list, add_messages]

def chatbot(state: FlightBookingState) -> FlightBookingState:
    formatted_prompt = prompt.format(
        messages=state["messages"],
        user_input=state["messages"][-1].content if state["messages"] else ""
    )
    response = llm.invoke(formatted_prompt, config={"callbacks": [langfuse_handler]})
    return {"messages": [response]}

graph_builder = StateGraph(state_schema=FlightBookingState)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START,"chatbot")
graph_builder.set_entry_point("chatbot")
graph_builder.set_finish_point("chatbot")
memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)

def stream_graph_updates(messages: str, session: str):
    for event in graph.stream({"messages": [{"role": "user", "content": messages}]},
    {"configurable": {"thread_id": session}},
    ):
        for value in event.values():
            return value["messages"][-1].content