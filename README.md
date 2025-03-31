# Tableau Langchain
#### Tableau tools for Agentic use cases with Langchain

This project builds Agentic tools from Tableau capabilities for use within the [Langchain](https://www.langchain.com/) and [LangGraph](https://langchain-ai.github.io/langgraph/tutorials/introduction/) frameworks. Solutions such as Tools, Utilities
and Chains are published to the PyPi registry under [langchain-tableau](https://pypi.org/project/langchain-tableau/) following conventions for [integrations](https://python.langchain.com/docs/contributing/how_to/integrations/) to Langchain.

We welcome you to explore how Agentic tools can drive alignment between your organization's data and the day to day needs of your users. Consider contributing to this project or creating your own work on a different framework, ultimately seek to increase the flow of data and help people get answers from it.

To see live demos of Agents using Tableau visit:
- [EmbedTableau.com](https://www.embedtableau.com/) | [Github Repository](https://github.com/Tab-SE/embedding_playbook) | [@stephenlprice](https://github.com/stephenlprice)

# Getting Started

The easiest way to get started with `tableau_langchain` is to try the Jupyter Notebooks found in the `experimental/notebooks/` folder. These examples will guide you through different use cases and scenarios with increasing complexity.

To use the solutions available at [langchain-tableau](https://pypi.org/project/langchain-tableau/) in notebooks and in your code do the following:

1. Install `langchain-tableau`

   ```bash
   pip install langchain-tableau
   ```
2. Import `langchain-tableau` and use it with your Agent

   ```python
    # langchain and langgraph package imports
    from langchain_openai import ChatOpenAI
    from langgraph.prebuilt import create_react_agent
    # langchain_tableau imports
    from langchain_tableau.tools.simple_datasource_qa import initialize_simple_datasource_qa

    # initialize an LLM
    llm = ChatOpenAI(model='gpt-4o-mini', temperature=0)

    # initalize `simple_datasource_qa` for querying a Tableau Published Datasource through VDS
    analyze_datasource = initialize_simple_datasource_qa(
        domain='https://your-tableau-cloud-or-server.com',
        site='Tableau site name',
        jwt_client_id='from an enabled Tableau Connected App',
        jwt_secret_id='from an enabled Tableau Connected App',
        jwt_secret='from an enabled Tableau Connected App',
        tableau_api_version='Tableau REST API version',
        tableau_user='user to query the Agent with',
        datasource_luid='unique data source ID can be obtained via REST or Metadata APIs',
        tooling_llm_model='model to use for the data query tool'
    )

    # add the tool to the array of tools used by the Agent
    tools = [ analyze_datasource ]

    # build the Agent using the minimum components (LLM + Tools)
    tableauAgent = create_react_agent(llm, tools)

    # Run the Agent
    messages = tableauAgent.invoke({"messages": [("human",'which states sell the most? Are those the same states with the most profits?')]})
   ```

## Experimental Sandbox

In order to develop and test solutions for the `langchain-tableau` package, this repository contains an `experimental/` folder organizing Agents, Tools, Utilities and other files that allow contributors to improve the solutions made available to the open-source community.

To use the sandbox, do the following:

1. Clone the repository

   ```bash
   git clone https://github.com/Tab-SE/tableau_langchain.git
   ```

2. Create a Python environment to isolate project dependencies (optional)

   Note: This is an example using Conda (environment.yml provided). If you use Conda skip to step #4 since dependencies will already be installed

   ```bash
   conda env create -f environment.yml
   conda activate tableau_langchain
   ```

3. Install project dependencies (use this with or without using Python environments)

   ```bash
   pip install
   ```

4. Declare Environment Variables

    Start by duplicating the template file:
    ```bash
    cp .env.template .env
    ```

    Replace the values in the `.env` file with your own

5. Run an Agent in the terminal

    ```bash
    python main.py
    ```

6. Run the Langgraph Server API in development mode

    ```bash
    langgraph dev
    ```

7. Run the Langgraph Server API via Docker

    ```bash
    langgraph build
    langgraph up
    ```

</br>

# About This Project

This repository is a monorepo with two components. The main goal is to publish and support a Langchain [integration](https://python.langchain.com/docs/contributing/how_to/integrations/). This produces a need to have a development sandbox to try these solutions before publishing them for open-source use.

## Published Agent Tools
The `pgk` folder contains production code shipped to the [PyPi registry](https://pypi.org/project/langchain-tableau/). These are
the currently available resources:

### Solutions
1. `simple_datasource_qa.py`
     - Query a Published Datasource in natural language
     - Leverage the analytical engine provided by Tableau's VizQL Data Service
       - Supports aggregating, filtering and soon: calcs!
       - Scales securely by way of the API interface preventing SQL injection

## Local Development
The `experimental` folder organizes agents, tools, utilities and notebooks for development and testing of solutions that may eventually be published ([see Published Agent Tools](#published-agent-tools)) for community use. This folder is essentially a sandbox for Tableau AI.


# Contributors

This the founding team for the project. Please consider contributing in your own way to further what's possible when you combine Tableau with AI Agents.

* [@stephenlprice](https://github.com/stephenlprice) - Lead Developer
* [@joeconstantino](https://github.com/joeconstantino) - Product Manager
* [@josephflu](https://github.com/josephflu) - Developer
* [@wjsutton](https://github.com/wjsutton) - Developer
* [@cristiansaavedra](https://github.com/cristiansaavedra) - Developer
