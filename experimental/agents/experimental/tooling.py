import os
from dotenv import load_dotenv

from experimental.tools.simple_datasource_qa import initialize_simple_datasource_qa

# from experimental.tools.external.retrievers import pinecone_retriever_tool
# from experimental.tools.external.web_search import tavily_tool

# Load environment variables before accessing them
load_dotenv()
tableau_domain = os.environ['TABLEAU_DOMAIN']
tableau_site = os.environ['TABLEAU_SITE']
tableau_jwt_client_id = os.environ['TABLEAU_JWT_CLIENT_ID']
tableau_jwt_secret_id = os.environ['TABLEAU_JWT_SECRET_ID']
tableau_jwt_secret = os.environ['TABLEAU_JWT_SECRET']
tableau_api_version = os.environ['TABLEAU_API_VERSION']
tableau_user = os.environ['TABLEAU_USER']
datasource_luid = os.environ['DATASOURCE_LUID']
model_provider = os.environ['MODEL_PROVIDER']
tooling_llm_model = os.environ['TOOLING_MODEL']

# Tableau VizQL Data Service Query Tool
analyze_datasource = initialize_simple_datasource_qa(
    domain=tableau_domain,
    site=tableau_site,
    jwt_client_id=tableau_jwt_client_id,
    jwt_secret_id=tableau_jwt_secret_id,
    jwt_secret=tableau_jwt_secret,
    tableau_api_version=tableau_api_version,
    tableau_user=tableau_user,
    datasource_luid=datasource_luid,
    model_provider=model_provider,
    tooling_llm_model=tooling_llm_model
)

# tableau_metrics = pinecone_retriever_tool(
#     name='tableau_metrics',
#     description="""Returns ML insights & predictive analytics on user-subscribed metrics
#     Prioritize using this tool if the user mentions metrics, KPIs, OKRs or similar

#     Make thorough queries for relevant context.
#     For a high level summary ask this way:
#     - start with requesting a KPI metrics summary
#     - dive deeper on those results using the methods for detailed metric info described below

#     For detailed metric info, ask using the target metric plus any of these topics:
#     - dimensions
#     - data
#     - descriptions
#     - drivers
#     - unusual changes
#     - trends
#     - sentiment
#     - current & previous values
#     - period over period change
#     - contributors
#     - detractors

#     NOT for precise data values. Use a data source query tool for specific values.
#     NOT for fetching data values on specific dates

#     Examples:
#     User: give me an update on my KPIs
#     Input: 'update on all KPIs, trends, sentiment"

#     User: what is going on with sales?
#     Input: 'sales trend, data driving sales, unusual changes, contributors, drivers and detractors'

#     User: what is the value of sales in 2024?
#     -> wrong usage of this tool, not for specific values
#     """,
#     pinecone_index = os.environ["METRICS_INDEX"],
#     model_provider = os.environ["MODEL_PROVIDER"],
#     embedding_model = os.environ["EMBEDDING_MODEL"],
#     text_key = "_node_content",
#     search_k = 6,
#     max_concurrency = 5
# )

# tableau_datasources = pinecone_retriever_tool(
#     name='tableau_datasources_catalog',
#     description="""Find the most relevant or useful Tableau data sources to answer the user query. Datasources often
#     have descriptions and fields that may match the needs of the user, use this information to determine the best data
#     resource for the user to consult.

#     Output is various chunks of text in vector format for summarization.

#     Args:
#         query (str): A natural language query describing the data to retrieve or an open-ended question
#         that can be answered using information contained in the data source

#     Returns:
#         dict: A data set relevant to the user's query
#     """,
#     pinecone_index=os.environ["DATASOURCES_INDEX"],
#     model_provider=os.environ["MODEL_PROVIDER"],
#     embedding_model=os.environ["EMBEDDING_MODEL"],
#     text_key = "_node_content",
#     search_k = 6,
#     max_concurrency = 5
# )

# tableau_analytics = pinecone_retriever_tool(
#     name='tableau_analytics_catalog',
#     description="""Find the most relevant or useful Tableau workbooks, dashboards, charts, reports and other forms
#     of visual analytics to help the user find canonical answers to their query. Unless the user specifically requests
#     for charts, workbooks, dashboards, etc. don't assume this is what they intend to find, if in doubt confirm by
#     letting them know you can search the catalog in their behalf.

#     If nothing matches the user's needs, then you might need to try a different approach such as querying a data source.

#     Output is various chunks of text in vector format for summarization.

#     Args:
#         query (str): A natural language query describing the data to retrieve or an open-ended question
#         that can be answered using information contained in the data source

#     Returns:
#         dict: A data set relevant to the user's query
#     """,
#     pinecone_index=os.environ["WORKBOOKS_INDEX"],
#     model_provider=os.environ["MODEL_PROVIDER"],
#     embedding_model=os.environ["EMBEDDING_MODEL"],
#     text_key = "_node_content",
#     search_k = 6,
#     max_concurrency = 5
# )



# List of tools used to build the state graph and for binding them to nodes
tools = [ analyze_datasource ]
