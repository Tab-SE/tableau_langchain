import os
import json
import re
import logging
from typing import Dict, Optional
from dotenv import load_dotenv

from experimental.utilities.vizql_data_service import query_vds, query_vds_metadata
from experimental.utilities.utils import json_to_markdown_table
from experimental.utilities.metadata import get_data_dictionary


import json
import logging

def get_headlessbi_data(payload, url: str, api_key: str, datasource_luid: str):
    # 1) Normalize payload to a dict
    if isinstance(payload, str):
        raw = payload.strip()
        if raw.startswith("```"):
            # drop the ```json and trailing ```
            lines = raw.splitlines()
            raw = "\n".join(lines[1:-1])
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as je:
            logging.error(f"JSON decoding error in get_headlessbi_data: {je}")
            raise ValueError("Invalid JSON format in the payload")

    # 2) Single call to query_vds
    try:
        headlessbi_data = query_vds(
            api_key=api_key,
            datasource_luid=datasource_luid,
            url=url,
            query=payload,    # always a dict now
        )

        if not headlessbi_data or 'data' not in headlessbi_data:
            raise ValueError("Invalid or empty response from query_vds")

        # 3) Convert to markdown and return
        markdown_table = json_to_markdown_table(headlessbi_data['data'])
        return markdown_table

    except ValueError as ve:
        logging.error(f"Value error in get_headlessbi_data: {ve}")
        raise

    except Exception as e:
        logging.error(f"Unexpected error in get_headlessbi_data: {e}")
        raise RuntimeError(f"An unexpected error occurred: {e}")



def get_payload(output):
    try:
        parsed_output = output.split('JSON_payload')[1]
    except IndexError:
        raise ValueError("'JSON_payload' not found in the output")

    match = re.search(r'{.*}', parsed_output, re.DOTALL)
    if match:
        json_string = match.group(0)
        try:
            payload = json.loads(json_string)
            return payload
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format in the payload")
    else:
        raise ValueError("No JSON payload found in the parsed output")


def get_values(api_key: str, url: str, datasource_luid: str, caption: str):
    column_values = {'fields': [{'fieldCaption': caption}]}
    output = query_vds(
        api_key=api_key,
        datasource_luid=datasource_luid,
        url=url,
        query=column_values
    )
    if output is None:
        return None
    sample_values = [list(item.values())[0] for item in output['data']][:4]
    return sample_values


def augment_datasource_metadata(
    task: str,
    api_key: str,
    url: str,
    datasource_luid: str,
    prompt: Dict[str, str],
    previous_errors: Optional[str] = None,
    previous_vds_payload: Optional[str] = None
):
    """
    Augment datasource metadata with additional information and format as JSON.

    This function retrieves the data dictionary and sample field values for a given
    datasource, adds them to the provided prompt dictionary, and includes any previous
    errors or queries for debugging purposes.

    Args:
        api_key (str): The API key for authentication.
        url (str): The base URL for the API endpoints.
        datasource_luid (str): The unique identifier of the datasource.
        prompt (Dict[str, str]): Initial prompt dictionary to be augmented.
        previous_errors (Optional[str]): Any errors from previous function calls. Defaults to None.
        previous_vds_payload (Optional[str]): The query that caused errors in previous calls. Defaults to None.

    Returns:
        str: A JSON string containing the augmented prompt dictionary with datasource metadata.

    Note:
        This function relies on external functions `get_data_dictionary` and `query_vds_metadata`
        to retrieve the necessary datasource information.
    """
    # insert the user input as a task
    prompt['task'] = task

    # get dictionary for the data source from the Metadata API
    data_dictionary = get_data_dictionary(
        api_key=api_key,
        domain=url,
        datasource_luid=datasource_luid
    )

    # insert data dictionary from Tableau's Data Catalog
    prompt['data_dictionary'] = data_dictionary['datasource_fields']
    # insert data source name, description and owner into 'meta' key
    del data_dictionary['datasource_fields']
    prompt['meta'] = data_dictionary

    #  get sample values for fields from VDS metadata endpoint
    datasource_metadata = query_vds_metadata(
        api_key=api_key,
        url=url,
        datasource_luid=datasource_luid
    )

    for field in datasource_metadata['data']:
        del field['fieldName']
        del field['logicalTableId']

    # insert the data model with sample values from Tableau's VDS metadata API
    prompt['data_model'] = datasource_metadata['data']

    # include previous error and query to debug in current run
    if previous_errors:
        prompt['previous_call_error'] = previous_errors
    if previous_vds_payload:
        prompt['previous_vds_payload'] = previous_vds_payload

    return prompt


def prepare_prompt_inputs(data: dict, user_string: str) -> dict:
    """
    Prepare inputs for the prompt template with explicit, safe mapping.

    Args:
        data (dict): Raw data from VizQL query
        user_input (str): Original user query

    Returns:
        dict: Mapped inputs for PromptTemplate
    """

    return {
        "vds_query": data.get('query', 'no query'),
        "data_source_name": data.get('data_source_name', 'no name'),
        "data_source_description": data.get('data_source_description', 'no description'),
        "data_source_maintainer": data.get('data_source_maintainer', 'no maintainer'),
        "data_table": data.get('data_table', 'no data'),
        "user_input": user_string
    }


def env_vars_simple_datasource_qa(
    domain=None,
    site=None,
    jwt_client_id=None,
    jwt_secret_id=None,
    jwt_secret=None,
    tableau_api_version=None,
    tableau_user=None,
    datasource_luid=None,
    model_provider=None,
    tooling_llm_model=None
):
    """
    Retrieves Tableau configuration from environment variables if not provided as arguments.

    Args:
        domain (str, optional): Tableau domain
        site (str, optional): Tableau site
        jwt_client_id (str, optional): JWT client ID
        jwt_secret_id (str, optional): JWT secret ID
        jwt_secret (str, optional): JWT secret
        tableau_api_version (str, optional): Tableau API version
        tableau_user (str, optional): Tableau user
        datasource_luid (str, optional): Datasource LUID
        tooling_llm_model (str, optional): Tooling LLM model

    Returns:
        dict: A dictionary containing all the configuration values
    """
    # Load environment variables before accessing them
    load_dotenv()

    config = {
        'domain': domain if isinstance(domain, str) and domain else os.environ['TABLEAU_DOMAIN'],
        'site': site or os.environ['TABLEAU_SITE'],
        'jwt_client_id': jwt_client_id or os.environ['TABLEAU_JWT_CLIENT_ID'],
        'jwt_secret_id': jwt_secret_id or os.environ['TABLEAU_JWT_SECRET_ID'],
        'jwt_secret': jwt_secret or os.environ['TABLEAU_JWT_SECRET'],
        'tableau_api_version': tableau_api_version or os.environ['TABLEAU_API_VERSION'],
        'tableau_user': tableau_user or os.environ['TABLEAU_USER'],
        'datasource_luid': datasource_luid or os.environ['DATASOURCE_LUID'],
        'model_provider': model_provider or os.environ['MODEL_PROVIDER'],
        'tooling_llm_model': tooling_llm_model or os.environ['TOOLING_MODEL']
    }

    return config
