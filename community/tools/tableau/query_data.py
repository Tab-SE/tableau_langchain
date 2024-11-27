import os

from pydantic import BaseModel, Field
from typing import Any, Dict, Tuple, Type, Optional

from langchain_core.tools import BaseTool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser

from langchain_openai import ChatOpenAI

from community.tools.tableau.prompts import headlessbi_prompt
from community.utilities.tableau.query_data import augment_datasource_metadata, get_headlessbi_data


class QueryInput(BaseModel):
    api_key: str = Field(description="API key for authentication to Tableau Headless BI")
    datasource_id: str = Field(description="ID of the Tableau datasource")
    datasource_metadata: Dict[str, Any] = Field(description="Metadata describing the dataset for accurate querying")
    endpoint: str = Field(description="Headless BI API endpoint for querying the datasource")
    query: str = Field(description="Detailed question about the dataset")


class QueryTableauData(BaseTool):
    # Must be unique within a set of tools provided to an LLM or agent.
    name: str = "query_tableau_datasource"
    # Describes what the tool does. Used as context by the LLM or agent.
    description: str = """
    A tool to query Tableau data sources on-demand using natural language.

    Human Users will regularly define friendly data models in Tableau that power business outcomes
    in the form of dashboards, metrics and other forms of analytics. Other Users rely on these
    analytical assets to answer questions needed to perform their job. These data models and
    business semantics translate into powerful Q&A and analytical resources for Agents.

    Input to this tool is a natural language query from a human User or external Agent as well as
    more details required to query the target Tableau data source via the VizQL Data Service using
    HTTP and JSON.

    Output is a resulting dataset containing only the fields of data, aggregations and calculations
    needed to answer the input query. The resulting dataset is represented in Markdown format to
    facilitate presentation in Chat UIs without requiring additional formatting by Agents that operate
    under limited context windows. Agents can present this output to end uses directly without modification
    or analyze the data for insights that can answer the user query depending on the implicit or explicit
    instructions and intent obtained from the user query.

    Args:
        query (str): A natural language query describing the data to retrieve or an open-ended question
        that can be answered using information contained in a Tableau data source.

    Returns:
        dict: A data set relevant to the user's query obtained from Tableau's VizQL Data Service
    """
    # Optional but recommended, and required if using callback handlers. It can be used to provide more information
    # (e.g., few-shot examples) or validation for expected parameters.
    args_schema: Type[BaseModel] = QueryInput


    def _run(self, api_key: str, datasource_id: str, datasource_metadata: Dict[str, Any], endpoint: str, query: str) -> Dict[str, Any]:
        # Logic to construct the query payload
        # Here you would implement the logic to create the JSON payload based on the inputs
        # For demonstration, we will create a simple payload
        payload = {
            "query": query,
            "datasource_id": datasource_id,
            "metadata": datasource_metadata
        }

        # Justification for the query
        query_plan = f"""
        The query was constructed to answer the question: '{query}'.
        It uses the datasource ID: {datasource_id} and includes relevant metadata.
        """

        # 1. Prompt template incorporating datasource metadata
        tool_prompt = augment_datasource_metadata(headlessbi_prompt)
        # passes instructions and metadata to Langchain prompt template
        active_prompt_template = ChatPromptTemplate.from_messages([
            SystemMessage(content=tool_prompt),
            ("user", "{query}")
        ])

        # 2. Language model settings
        llm = ChatOpenAI(model=os.environ['AGENT_MODEL'], temperature=0)

        # 3. Query Data
        headlessbi_data = get_headlessbi_data

        # 4. Standard Langchain string parser for terminal outputs
        output_parser = StrOutputParser()

        # 5. Standard Langchain string parser for API responses
        json_parser = JsonOutputParser()

        # this chain defines the flow of data through the system
        chain = active_prompt_template | llm | headlessbi_data

        # Return the structured output
        return {
            "query_plan": query_plan,
            "payload": payload
        }