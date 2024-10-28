import os

from langchain_openai import ChatOpenAI

from agents.research_agent.state import ResearchAgentState
from agents.research_agent.tooling import equip_tooling


def chatbot(state: ResearchAgentState):
    """
    Graph Node
    Takes the current State as input and returns a dictionary containing an updated messages list
    under the key "messages". This is the basic pattern for all LangGraph node functions.
    """
    llm_config = ChatOpenAI(
        model=os.environ["AGENT_MODEL"],
        api_key=os.environ["OPENAI_API_KEY"],
        temperature=0,
        verbose=True,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        # allow_dangerous_code=True,
    )

    tools = equip_tooling()

    llm = llm_config.bind_tools(tools)

    return {"messages": [llm.invoke(state["messages"])]}
