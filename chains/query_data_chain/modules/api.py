import logging

from langchain.chains import TransformChain
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

# Set up the logger for this module
logger = logging.getLogger(__name__)

def vds_query():
    # sets up parser to respond with reliable outputs
   parser = JsonOutputParser(pydantic_object=VDS_Query_Response)
   return parser

# Define the data structure for the response
class VDS_Query_Response(BaseModel):
    data: str = Field(description="the table of data containing the response to the query")
    behavioral: str = Field(description="a behavioral summary of the reasoning and explanation behind the action taken")


def vds_transform(parameters: dict) -> dict:
    response = TransformChain(
        input_variables=["pandas_agent_output"],
        output_variables=["analysis"],
        transform=create_response,
        atransform=create_response_async
    )

    return response


def create_response(parameters: dict) -> dict:
    # split the string before and after data
    split_string = parameters['pandas_agent_output'].split('\n\n|', 1)
    # store behavioral data in natural language
    pandas_behavioral = split_string[0]
    logger.info(f"******* pandas_behavior *******\n{str(pandas_behavioral)}")
    # add back the '|' character and extract the data
    pandas_data = '|' + split_string[1] if len(split_string) > 1 else ''
    logger.info(f"******* data *******\n{pandas_data}")

    response_template = {
        'analysis': {
            'analyst_behavior': pandas_behavioral,
            'analyst_result': pandas_data
        }
    }

    return response_template

async def create_response_async(parameters: dict) -> dict:
    # split the string before and after data
    split_string = parameters['pandas_agent_output'].split('\n\n|', 1)
    # store behavioral data in natural language
    pandas_behavioral = split_string[0]
    logger.info(f"******* pandas_behavior *******\n{str(pandas_behavioral)}")
    # add back the '|' character and extract the data
    pandas_data = '|' + split_string[1] if len(split_string) > 1 else ''
    logger.info(f"******* data *******\n{pandas_data}")

    response_template = {
        'analysis': {
            'analyst_behavior': pandas_behavioral,
            'analyst_result': pandas_data
        }
    }

    return response_template
