import json
from typing import Optional
from pydantic import BaseModel, Field

from langchain.prompts import PromptTemplate
from langchain_core.tools import tool, ToolException

from experimental.tools.prompts import vds_query, vds_prompt_data, vds_response
from experimental.utilities.auth import jwt_connected_app
from experimental.utilities.models import select_model
from experimental.utilities.simple_datasource_qa import (
    env_vars_simple_datasource_qa,
    augment_datasource_metadata,
    get_headlessbi_data,
    prepare_prompt_inputs
)


class DataSourceQAInputs(BaseModel):
    """Describes inputs for usage of the simple_datasource_qa tool"""

    user_input: str = Field(
        ...,
        description="""Describe the user query thoroughly in natural language such as: 'orders and sales for April 20 2025'.
        You can ask for relative dates such as last week, 3 days ago, current year, previous 3 quarters or
        specific dates: profits and average discounts for last week""",
        examples=[
            "sales and orders for April 20 2025"
        ]
    )
    previous_call_error: Optional[str] = Field(
        None,
        description="""If the previous interaction resulted in a VizQL Data Service error, include the error otherwise use None:
        Error: Quantitative Filters must have a QuantitativeFilterType""",
        examples=[
            None, # no errors example
            "Error: Quantitative Filters must have a QuantitativeFilterType"
        ],
    )
    previous_vds_payload: Optional[str] = Field(
        None,
        description="""If the previous interaction resulted in a VizQL Data Service error, include the faulty VDS JSON payload
        otherwise use None: {\"fields\":[{\"fieldCaption\":\"Sub-Category\",\"fieldAlias\":\"SubCategory\",\"sortDirection\":\"DESC\",
        \"sortPriority\":1},{\"function\":\"SUM\",\"fieldCaption\":\"Sales\",\"fieldAlias\":\"TotalSales\"}],
        \"filters\":[{\"field\":{\"fieldCaption\":\"Order Date\"},\"filterType\":\"QUANTITATIVE_DATE\",\"minDate\":\"2023-04-01\",
        \"maxDate\":\"2023-10-01\"},{\"field\":{\"fieldCaption\":\"Sales\"},\"filterType\":\"QUANTITATIVE_NUMERICAL\",
        \"quantitativeFilterType\":\"MIN\",\"min\":200000},{\"field\":{\"fieldCaption\":\"Sub-Category\"},\"filterType\":\"MATCH\",
        \"exclude\":true,\"contains\":\"Technology\"}]}""",
        examples=[
            None, # no errors example
            "{\"fields\":[{\"fieldCaption\":\"Sub-Category\",\"fieldAlias\":\"SubCategory\",\"sortDirection\":\"DESC\",\"sortPriority\":1},{\"function\":\"SUM\",\"fieldCaption\":\"Sales\",\"fieldAlias\":\"TotalSales\"}],\"filters\":[{\"field\":{\"fieldCaption\":\"Order Date\"},\"filterType\":\"QUANTITATIVE_DATE\",\"minDate\":\"2023-04-01\",\"maxDate\":\"2023-10-01\"},{\"field\":{\"fieldCaption\":\"Sales\"},\"filterType\":\"QUANTITATIVE_NUMERICAL\",\"quantitativeFilterType\":\"MIN\",\"min\":200000},{\"field\":{\"fieldCaption\":\"Sub-Category\"},\"filterType\":\"MATCH\",\"exclude\":true,\"contains\":\"Technology\"}]}"
        ],
    )


def initialize_simple_datasource_qa(
    domain: Optional[str] = None,
    site: Optional[str] = None,
    jwt_client_id: Optional[str] = None,
    jwt_secret_id: Optional[str] = None,
    jwt_secret: Optional[str] = None,
    tableau_api_version: Optional[str] = None,
    tableau_user: Optional[str] = None,
    datasource_luid: Optional[str] = None,
    model_provider: Optional[str] = None,
    tooling_llm_model: Optional[str] = None
):
    """
    Initializes the Langgraph tool called 'simple_datasource_qa' for analytical
    questions and answers on a Tableau Data Source

    Args:
        domain (Optional[str]): The domain of the Tableau server.
        site (Optional[str]): The site name on the Tableau server.
        jwt_client_id (Optional[str]): The client ID for JWT authentication.
        jwt_secret_id (Optional[str]): The secret ID for JWT authentication.
        jwt_secret (Optional[str]): The secret for JWT authentication.
        tableau_api_version (Optional[str]): The version of the Tableau API to use.
        tableau_user (Optional[str]): The Tableau user to authenticate as.
        datasource_luid (Optional[str]): The LUID of the data source to perform QA on.
        tooling_llm_model (Optional[str]): The LLM model to use for tooling operations.

    Returns:
        function: A decorated function that can be used as a langgraph tool for data source QA.

    The returned function (datasource_qa) takes the following parameters:
        user_input (str): The user's query or command represented in simple SQL.
        previous_call_error (Optional[str]): Any error from a previous call, for error handling.

    It returns a dictionary containing the results of the QA operation.

    Note:
        If arguments are not provided, the function will attempt to read them from
        environment variables, typically stored in a .env file.
    """
    # if arguments are not provided, the tool obtains environment variables directly from .env
    env_vars = env_vars_simple_datasource_qa(
        domain=domain,
        site=site,
        jwt_client_id=jwt_client_id,
        jwt_secret_id=jwt_secret_id,
        jwt_secret=jwt_secret,
        tableau_api_version=tableau_api_version,
        tableau_user=tableau_user,
        datasource_luid=datasource_luid,
        model_provider=model_provider,
        tooling_llm_model=tooling_llm_model
    )

    @tool("simple_datasource_qa", args_schema=DataSourceQAInputs)
    def simple_datasource_qa(
        user_input: str,
        previous_call_error: Optional[str] = None,
        previous_vds_payload: Optional[str] = None
    ) -> dict:
        """
        Queries a Tableau data source for analytical Q&A. Returns a data set you can use to answer user questions.
        To be more efficient, describe your entire query in a single request rather than selecting small slices of
        data in multiple requests. DO NOT perform multiple queries if all the data can be fetched at once with the
        same filters or conditions:

        Good query: "Profits & average discounts by region for last week"
        Bad queries: "profits per region last week" & "average discounts per region last week"

        If you received an error after using this tool, mention it in your next attempt to help the tool correct itself.
        """

        # Session scopes are limited to only required authorizations to Tableau resources that support tool operations
        access_scopes = [
            "tableau:content:read", # for quering Tableau Metadata API
            "tableau:viz_data_service:read" # for querying VizQL Data Service
        ]
        try:
            tableau_session = jwt_connected_app(
                tableau_domain=env_vars["domain"],
                tableau_site=env_vars["site"],
                jwt_client_id=env_vars["jwt_client_id"],
                jwt_secret_id=env_vars["jwt_secret_id"],
                jwt_secret=env_vars["jwt_secret"],
                tableau_api=env_vars["tableau_api_version"],
                tableau_user=env_vars["tableau_user"],
                scopes=access_scopes
            )
        except Exception as e:
            auth_error_string = f"""
            CRITICAL ERROR: Could not authenticate to the Tableau site successfully.
            This tool is unusable as a result.
            Error from remote server: {e}

            INSTRUCTION: Do not ask the user to provide credentials directly or in chat since they should
            originate from a secure Connected App or similar authentication mechanism. You may inform the
            user that you are not able to access their Tableau environment at this time. You can also describe
            the nature of the error to help them understand why you can't service their request.
            """
            raise ToolException(auth_error_string)

        # credentials to access Tableau environment on behalf of the user
        tableau_auth =  tableau_session['credentials']['token']

        # Data source for VDS querying
        tableau_datasource = env_vars["datasource_luid"]

        # 0. Obtain metadata about the data source to enhance the query writing prompt
        query_writing_data = augment_datasource_metadata(
            task = user_input,
            api_key = tableau_auth,
            url = domain,
            datasource_luid = tableau_datasource,
            prompt = vds_prompt_data,
            previous_errors = previous_call_error,
            previous_vds_payload = previous_vds_payload
        )

        # 1. Insert instruction data into the template
        query_writing_prompt = PromptTemplate(
            input_variables=[
                "task"
                "instructions",
                "vds_schema",
                "sample_queries",
                "error_queries",
                "data_dictionary",
                "data_model",
                "previous_call_error",
                "previous_vds_payload"
            ],
            template=vds_query
        )

        # 2. Instantiate language model to execute the prompt to write a VizQL Data Service query
        query_writer = select_model(
            provider=env_vars["model_provider"],
            model_name=env_vars["tooling_llm_model"],
            temperature=0
        )

        # 3. Query data from Tableau's VizQL Data Service using the AI written payload
        def get_data(vds_query):
            payload = vds_query.content

            try:
                data = get_headlessbi_data(
                    api_key = tableau_auth,
                    url = domain,
                    datasource_luid = tableau_datasource,
                    payload = payload
                )

                return {
                    "vds_query": payload,
                    "data_table": data,
                }
            except Exception as e:
                query_error_message = f"""
                Tableau's VizQL Data Service return an error for the generated query:

                {str(vds_query.content)}

                The user_input used to write this query was:

                {str(user_input)}

                This was the error:

                {str(e)}

                Consider retrying this tool with the same inputs but include the previous query
                causing the error and the error itself for the tool to correct itself on a retry.
                If the error was an empty array, this usually indicates an incorrect filter value
                was applied, thus returning no data
                """

                raise ToolException(query_error_message)

        # 4. Prepare inputs for a structured response to the calling Agent
        def response_inputs(input):
            metadata = query_writing_data.get('meta')
            data = {
                "query": input.get('vds_query', ''),
                "data_source_name": metadata.get('datasource_name'),
                "data_source_description": metadata.get('datasource_description'),
                "data_source_maintainer": metadata.get('datasource_owner'),
                "data_table": input.get('data_table', ''),
            }
            inputs = prepare_prompt_inputs(data=data, user_string=user_input)
            return inputs

        # 5. Response template for the Agent with further instructions
        response_prompt = PromptTemplate(
            input_variables=[
                "data_source_name",
                "data_source_description",
                "data_source_maintainer",
                "vds_query",
                "data_table",
                "user_input"
            ],
            template=vds_response
        )

        # this chain defines the flow of data through the system
        chain = query_writing_prompt | query_writer | get_data | response_inputs | response_prompt


        # invoke the chain to generate a query and obtain data
        vizql_data = chain.invoke(query_writing_data)

        # Return the structured output
        return vizql_data

    return simple_datasource_qa
