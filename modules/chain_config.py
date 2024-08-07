import os, json

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain.chains import TransformChain

from modules import metadata
from prompts import nlq_to_vds
from agents import pandas

# defines the langtab chain
def create_chain():
    # 1. Prompt template
    datasource_metadata = metadata.read()
    nlq_to_vds.prompt['data_model'] = datasource_metadata
    headless_bi_prompt_string = json.dumps(nlq_to_vds.prompt)

    active_prompt_template = ChatPromptTemplate.from_messages([
        SystemMessage(content=headless_bi_prompt_string),
        ("user", "{query}")
    ])

    # 2. Chat model
    llm = ChatOpenAI(model=os.environ['VDS_AGENT_MODEL'])

    # 3. Parser
    output_parser = StrOutputParser()

    # 4. Pandas agent
    pandas_agent = TransformChain(
        input_variables=["query"],
        output_variables=["analysis"],
        transform=pandas.analyze
    )

    chain = active_prompt_template | llm | output_parser | pandas_agent

    return chain
