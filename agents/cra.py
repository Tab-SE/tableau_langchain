
import os
from typing import Literal, TypedDict, Annotated, Sequence

from langchain_openai import ChatOpenAI

from langchain_core.tools import tool
from langchain_core.messages import BaseMessage

from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent, InjectedStore
from langgraph.managed import IsLastStep
from langgraph.store.base import BaseStore

# Tableau Community tools
from community.langchain_community.tools.tableau.query_data import query_data
# other tools
from community.langchain_community.tools.others import llamaindex_pinecone_retriever, tavily_tool

from agents.utils import  _visualize_graph


def initialize_agent(memory_store):
    """
    TABLEAU CRA AGENT

    This Agent uses the Langgraph prebuilt `create_react_agent` to can handle conversations on Tableau subjects such as:
        - Metrics (canonical source of truth for metrics, includes machine learning insights generated by Tableau Pulse)
        - Workbooks (contains analytics such as dashboards and charts that server as canonical interfaces for data exploration)
        - Data Sources (describes sources of data available for querying and exploration)
        - Headless BI (can query a data source for on-demand data sets including aggregations, filters and calculations)
        - Web Search (can incorporate external knowledge from the web)
        - Weather (can provide current weather reports on certain cities)

    Intended the most straightforward implementation of Tableau tooling for Langgraph.
    """

    # define custom state for the cra agent
    class CustomState(TypedDict):
        messages: Annotated[Sequence[BaseMessage], add_messages]
        is_last_step: IsLastStep
        user_context: str
        application_context: str
        language: str
        tableau_credentials: dict

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

    # incorporate all agent tools
    # Knowledge Base tool
    knowledge_base = llamaindex_pinecone_retriever

    # Tableau VizQL Data Service Query Tool
    query_datasource = query_data

    # Web Search tool
    web_search = tavily_tool()

    # For demonstration purposes, this tool returns pre-defined values for weather in 3 cities
    @tool
    def get_weather(city: Literal["nyc", "sf", "atx", "sea"]):
        """
        Use this to get weather information. If the city is not provided ask the user to confirm which city
        they want to know more about from the list of available cities.
        """
        if city == "nyc":
            return "It might be cloudy in New York, NY"
        elif city == "sf":
            return "It's always sunny in San Francisco, CA"
        elif city == "atx":
            return "It's running hot in Austin, TX"
        elif city == "sea":
            return "It's quite rainy in Seattle, WA"
        else:
            raise AssertionError("Unknown city")

    # List all tools used to build the state graph and for binding them to nodes
    tools = [ knowledge_base, query_datasource, web_search, get_weather ]

    if os.getenv('DEBUG') == '1':
        debugging = True
    else:
        debugging = False

    # Define the agent graph
    cra_agent = create_react_agent(
        model=llm,
        state_schema=CustomState,
        tools=tools,
        store=memory_store,
        debug=debugging
    )

    # outputs a mermaid diagram of the graph in png format
    _visualize_graph(cra_agent)

    return cra_agent
