from langgraph.graph import StateGraph,START,END
from langgraph.checkpoint.memory import MemorySaver
from app.agents.state import AgentState
from app.agents.nodes.palnner import planner_node
from app.agents.nodes.retriever import retrieve_node
from app.agents.nodes.responder import generate_node

workflow= StateGraph(AgentState)

workflow.add_node("planner", planner_node)
workflow.add_node("retriever", retrieve_node)
workflow.add_node("responder", generate_node)


workflow.set_entry_point("planner")

def route_planner(state: AgentState):
    """
    Routes the workflow based on the planner's decision.
    """
    if state["current_query"] == "CONVERSATIONAL":
        return "responder"
    return "retriever"

workflow.set_entry_point("planner")

# Conditional Edge: Planner -> Router -> (Retriever OR Responder)
workflow.add_conditional_edges(
    "planner",
    route_planner,
    {
        "retriever": "retriever",
        "responder": "responder"
    }
)


workflow.add_edge("retriever", "responder")
workflow.add_edge("responder", END)


# MemorySaver allows the agent to remember conversations based on 'thread_id'
checkpointer = MemorySaver()


# 4. Compile the Graph with Memory
rag_agent = workflow.compile(checkpointer=checkpointer)