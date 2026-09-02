from app.agents.state import AgentState
from app.gateway import generate
import logfire


async def planner_node(state: AgentState):
    user_message = state["messages"][-1]["content"]

    prompt = f"""
You are the READFLIX Library assistant.

Decide what to do with the user's latest message:

- Return CONVERSATIONAL for greetings, simple conversation,
  or questions answerable from the conversation.
- Otherwise return a concise search query for READFLIX information.

User: {user_message}

Output ONLY:
CONVERSATIONAL
or
a search query.
"""

    with logfire.span("🧭 Planner"):
        response = await generate(
            [{"role": "user", "content": prompt}],
            feature="planner",
        )

        decision = response.choices[0].message.content.strip()

        logfire.info(
            "🧭 Planner decision",
            decision=decision,
        )

    if decision == "CONVERSATIONAL":
        return {
            "current_query": "CONVERSATIONAL",
            "status": "Conversational response",
            "plan": ["Retrieval skipped"],
        }

    return {
        "current_query": decision,
        "status": "Retrieval required",
        "plan": [f"Search: {decision}"],
    }