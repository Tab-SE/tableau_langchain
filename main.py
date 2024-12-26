import os, asyncio

from dotenv import load_dotenv

from agents.cra.agent import initialize_agent
from agents.utils.agent_utils import stream_graph_updates
from agents.utils.tableau import authenticate_tableau_user
from agents.utils.other import _set_env


async def main():
    """
    TABLEAU AGENT STAGING PLATFORM

    Stage individual LangGraph Agents and Tableau AI tools to test functionality such as:
        - Metrics (canonical source of truth for metrics, includes machine learning insights generated by Tableau Pulse)
        - Workbooks (contains analytics such as dashboards and charts that server as canonical interfaces for data exploration)
        - Data Sources (describes sources of data available for querying and exploration)
        - Headless BI (can query a data source for on-demand data sets including aggregations, filters and calculations)
        - Web Search (can incorporate external knowledge from the web)

    Execute behavior within different agentic architectures
    """
    # environment variables available to current process and sub processes
    load_dotenv()

    # checks for values in .env, else prompts user before initializing
    _set_env('OPENAI_API_KEY')
    _set_env('TABLEAU_DOMAIN')
    _set_env('TABLEAU_SITE')
    _set_env('DATASOURCE_LUID')
    _set_env('TAVILY_API_KEY')
    _set_env('PINECONE_API_KEY')
    _set_env('PINECONE_ENVIRONMENT')
    _set_env('PINECONE_INDEX_NAME')
    _set_env('RETRIEVER_MODEL')

    domain = os.environ['TABLEAU_DOMAIN']
    site = os.environ['TABLEAU_SITE']
    datasource_luid = os.environ['DATASOURCE_LUID']

    # define required authorizations to Tableau resources to support Agent operations
    access_scopes = [
        "tableau:content:read", # for quering Tableau Metadata API
        "tableau:viz_data_service:read" # for querying VizQL Data Service
    ]

    tableau_session = await authenticate_tableau_user(
        jwt_client_id=os.environ['TABLEAU_JWT_CLIENT_ID'],
        jwt_secret_id=os.environ['TABLEAU_JWT_SECRET_ID'],
        jwt_secret=os.environ['TABLEAU_JWT_SECRET'],
        tableau_api=os.environ['TABLEAU_API'],
        tableau_user=os.environ['TABLEAU_USER'],
        tableau_domain=domain,
        tableau_site=site,
        scopes=access_scopes
    )

    sample_inputs = {
        'tableau_credentials': {
            "session": tableau_session,
            "url": domain,
            "site": site,
        },
        'datasource': {
            "luid": datasource_luid,
            "name": None,
            "description": None
        },
        'workbook': {
            "luid": None,
            "name": None,
            "description": None,
            'sheets': None,
            'viz_url': None
        },
        'rag': {
            'analytics': {
                "metrics": None,
                "workbooks": None,
                "datasources": None
            },
            'knowledge_base': {
                "tableau": None,
                "agent": None,
                'app': None
            }
        }
    }

    # initialize one of the repo's custom agents
    agent = initialize_agent(agent_inputs=sample_inputs)

    print("\nWelcome to the Tableau Agent Staging Environment!")
    print("Enter a prompt or type 'exit' to end \n")

    # User input loop
    while True:
        try:
            user_input = input("User: \n").strip()  # Use .strip() to remove leading/trailing whitespace

            if user_input.lower() in ["quit", "exit", "q", "stop", "end"]:
                print("Exiting Tableau Agent Staging Environment...")
                print("Goodbye!")
                break

            # If user input is empty, set to default string
            if not user_input:
                user_input = "show me average discount, total sales and profits by region sorted by profit\n"
                print("Test input: " + user_input)

            message = {
                "user_message": user_input,
            }

            stream_graph_updates(message, agent)

        except Exception as e:
            print(f"An error occurred: {e}")
            # Use diagnostic string in case of an error
            user_input = f"The previous operation failed with this error: {e}.\n Write a query to test this tool again and describe the issue"
            print("Retrying with diagnostics input: " + user_input)

            message = {
                "user_message": user_input,
            }

            stream_graph_updates(message, agent)
            break

if __name__ == "__main__":
    asyncio.run(main())
