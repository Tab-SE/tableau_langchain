import os
from dotenv import load_dotenv

from experimental.tools.simple_datasource_qa import initialize_simple_datasource_qa

from experimental.tools.external.retrievers import pinecone_retriever_tool
from experimental.tools.external.web_search import tavily_tool

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

tableau_metrics = pinecone_retriever_tool(
    name='tableau_metrics',
    description="""Returns ML insights on user-subscribed metrics
    Prioritize using this tool if the user mentions metrics, KPIs, OKRs or similar

    Make thorough queries for relevant context.
    Use "metrics update" for a summary. For detailed metric info, ask about:
    - dimensions
    - data
    - descriptions
    - drivers
    - unusual changes
    - trends
    - sentiment
    - current & previous values
    - period over period change
    - contributors
    - detractors

    NOT for precise data values. Use a data source query tool for specific values.
    NOT for fetching data values on specific dates

    Examples:
    User: give me an update on my KPIs
    Input: 'update on all KPIs, trends, sentiment"

    User: what is going on with sales?
    Input: 'sales trend, data driving sales, unusual changes, contributors, drivers and detractors'

    User: what is the value of sales in 2024?
    -> wrong usage of this tool, not for specific values
    """,
    pinecone_index=os.environ["METRICS_INDEX"],
    model_provider=os.environ["MODEL_PROVIDER"],
    embedding_model=os.environ["EMBEDDING_MODEL"]
)


# Web Search tool
web_search = tavily_tool()

# List of tools used to build the state graph and for binding them to nodes
tools = [ analyze_datasource, tableau_metrics, web_search ]
