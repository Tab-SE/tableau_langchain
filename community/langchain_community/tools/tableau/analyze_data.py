import os
from typing import Dict, Annotated

from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage

from langchain_openai import ChatOpenAI

from langgraph.prebuilt import InjectedState

from community.langchain_community.tools.tableau.prompts import vds_prompt, vds_prompts
from community.langchain_community.utilities.tableau.analyze_data import AnalyzeDataInputs, augment_datasource_metadata, get_filter_values, get_headlessbi_data

@tool("analyze_tableau_datasource")
async def analyze_data(
    query: str,
    tableau_credentials: Annotated[Dict, InjectedState("tableau_credentials")],
    datasource_state: Annotated[Dict, InjectedState("datasource")]
) -> dict:
    """
    Queries Tableau data sources for analytical Q&A. Returns a data set you can use to answer user questions.
    You need a data source to target to use this tool. If a target data source is unknown, use a data source
    search tool to find the right resource and retry with more information or ask the user to provide it.

    Prioritize this tool if the user asks you to analyze and explore data. This tool includes Agent summarization
    and is not meant for direct data set exports. To be more efficient, query all the data you need in a single
    request rather than selecting small slices of data in multiple requests
    """

    # credentials to access Tableau environment on behalf of the user
    tableau_auth =  tableau_credentials['session']
    tableau_url = tableau_credentials['url']
    if not tableau_auth or not tableau_url:
        # lets the Agent know this error cannot be resolved by the end user
        raise KeyError("Critical Error: Tableau credentials were not provided by the client application. INSTRUCTION: Do not ask the user to provide credentials directly or in chat since they should come from a secure application.")

    # Getting data source for VDS querying from InjectedState
    tableau_datasource = datasource_state['luid'] if datasource_state and 'luid' in datasource_state else None

    # Check if we have a valid datasource
    if not tableau_datasource:
        # Lets the Agent know that the LUID is missing and it needs to use an alternative tool
        raise KeyError("The Datasource LUID is missing. Use a data source search tool to find an appropriate query target that matches the user query.")

    # Obtain metadata about the data source fields and sample values
    datasource_metadata = await augment_datasource_metadata(
        api_key = tableau_auth,
        url = tableau_url,
        datasource_luid = tableau_datasource
    )

    # add the metadata to prompts used for each generation phase
    vds_prompts['fields_prompt'] += datasource_metadata
    vds_prompts['filters_prompt'] += datasource_metadata
    vds_prompts['calculations_prompt'] += datasource_metadata

    # Instantiate language model to execute query generation prompts
    query_writer = ChatOpenAI(
        model=os.getenv('TOOLING_MODEL'),
        temperature=0
    )

    # Langchain chat template for writing fields
    fields_prompt = ChatPromptTemplate.from_messages([
        SystemMessage(vds_prompts['fields_prompt']),
        ("user", "{utterance}")
    ])

    # Augments the filtering prompt dynamically with categorical filters
    async def filter_values(fields_generation):
        values = await get_filter_values(
            api_key = tableau_auth,
            url = tableau_url,
            datasource_luid = tableau_datasource,
            fields = fields_generation.content
        )
        vds_prompts['filters_prompt'] += values

        # Langchain chat template for writing filters
        filters_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(vds_prompts['filters_prompt']),
            ("user", "{utterance}")
        ])
        return filters_prompt

    # Langchain chat template for writing calculations
    calculations_prompt = ChatPromptTemplate.from_messages([
        SystemMessage(vds_prompts['calculations_prompt']),
        ("user", "{utterance}")
    ])

    # Query data from Tableau's VizQL Data Service using the dynamically written payload
    async def get_data(vds_query):
        return await get_headlessbi_data(
            api_key = tableau_auth,
            url = tableau_url,
            datasource_luid = tableau_datasource,
            payload = vds_query.content
        )

    # this chain defines the flow of data through the system
    chain = fields_prompt | query_writer | filter_values | query_writer | calculations_prompt | query_writer | get_data

    # invoke the chain to generate a query and obtain data
    vizql_data = await chain.ainvoke(query)

    # Return the structured output
    return vizql_data
