
import os
from typing import Literal

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

from langgraph.prebuilt import create_react_agent

# Tableau Community tools
from community.langchain_community.tools.tableau.query_data import get_data
# other tools
from community.langchain_community.tools.others import llamaindex_pinecone_retriever, tavily_tool

from agents.utils import  _visualize_graph


def initialize_agent(chatbot_store):
    """
    TABLEAU CRA AGENT

    This Agent uses the Langgraph prebuilt `create_react_agent` to can handle conversations on Tableau subjects such as:
        - Metrics (canonical source of truth for metrics, includes machine learning insights generated by Tableau Pulse)
        - Workbooks (contains analytics such as dashboards and charts that server as canonical interfaces for data exploration)
        - Data Sources (describes sources of data available for querying and exploration)
        - Headless BI (can query a data source for on-demand data sets including aggregations, filters and calculations)
        - Web Search (can incorporate external knowledge from the web)

    Intended the most straightforward implementation of Tableau tooling for Langgraph.
    """

    model = ChatOpenAI(
        model=os.environ["AGENT_MODEL"],
        api_key=os.environ["OPENAI_API_KEY"],
        temperature=0,
        verbose=True,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        # allow_dangerous_code=True,
    )

    # For this tutorial we will use custom tool that returns pre-defined values for weather in two cities (NYC & SF)
    @tool
    def get_weather(city: Literal["nyc", "sf"]):
        """Use this to get weather information."""
        if city == "nyc":
            return "It might be cloudy in nyc"
        elif city == "sf":
            return "It's always sunny in sf"
        else:
            raise AssertionError("Unknown city")

    # Knowledge Base tool
    knowledge_base = llamaindex_pinecone_retriever

    # Tableau VizQL Data Service Query Tool
    query_datasource = get_data

    # Web Search tool
    web_search = tavily_tool()

    # List of tools used to build the state graph and for binding them to nodes
    tools = [knowledge_base, web_search, get_weather]

    # Define the graph
    cra_agent = create_react_agent(model, tools=tools)

    # outputs a mermaid diagram of the graph in png format
    _visualize_graph(cra_agent)

    return cra_agent
