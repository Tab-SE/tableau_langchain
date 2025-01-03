from typing import Any
import os

from langchain_openai import ChatOpenAI

from langgraph.prebuilt import create_react_agent
from langgraph.store.memory import InMemoryStore

from agents.cra.state import TableauAgentState
from agents.cra.tooling import tools


def initialize_agent() -> Any:
    """
    TABLEAU CRA AGENT

    This Agent uses the Langgraph prebuilt `create_react_agent` to can handle conversations on Tableau subjects such as:
        - Metrics (canonical source of truth for metrics, includes machine learning insights generated by Tableau Pulse)
        - Workbooks (contains analytics such as dashboards and charts that server as canonical interfaces for data exploration)
        - Data Sources (describes sources of data available for querying and exploration)
        - VizQL Data Service (can query a data source for on-demand data sets including aggregations, filters and calculations)
        - Web Search (can incorporate external knowledge from the web)

    Intended the most straightforward implementation of Tableau tooling for Langgraph.
    """

    # configure running model for the agent
    llm = ChatOpenAI(
        model=os.environ["AGENT_MODEL"],
        api_key=os.environ["OPENAI_API_KEY"],
        temperature=0,
        verbose=True,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        # allow_dangerous_code=True,
    )

    # initialize a memory store
    memory = InMemoryStore()

    # set agent debugging state
    if os.getenv('DEBUG') == '1':
        debugging = True
    else:
        debugging = False

    # define the agent graph
    cra_agent = create_react_agent(
        model=llm,
        state_schema=TableauAgentState,
        tools=tools,
        store=memory,
        debug=debugging
    )

    return cra_agent
