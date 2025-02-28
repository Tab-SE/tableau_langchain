import json
import requests
from typing import Dict
from langchain_tableau.utilities.utils import http_post


def get_datasource_query(luid):
    query = f"""
    query Datasources {{
      publishedDatasources(filter: {{ luid: "{luid}" }}) {{
        name
        description
        isCertified
        owner {{
          username
          name
          email
        }}
        hasActiveWarning
        dataQualityWarnings {{
          authorDisplayName
          isActive
          isElevated
          value
          category
          message
          createdAt
          updatedAt
        }}
        extractLastRefreshTime
        extractLastIncrementalUpdateTime
        extractLastUpdateTime
        datasourceFilters {{
          field {{
            name
            description
          }}
        }}
        fields {{
          name
          description
        }}
      }}
    }}
    """

    return query


async def get_data_dictionary_async(api_key: str, domain: str, datasource_luid: str) -> Dict:
    full_url = f"{domain}/api/metadata/graphql"

    query = get_datasource_query(datasource_luid)

    payload = json.dumps({
        "query": query,
        "variables": {}
    })

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-Tableau-Auth': api_key
    }

    response = await http_post(endpoint=full_url, headers=headers, payload=payload)

    # Check if the request was successful (status code 200)
    if response['status'] == 200:
        return response['data']
    else:
        error_message = (
            f"Failed to query Tableau's Metadata API"
            f"Status code: {response['status']}. Response: {response['data']}"
        )
        raise RuntimeError(error_message)


def get_data_dictionary(api_key: str, domain: str, datasource_luid: str) -> Dict:
    full_url = f"{domain}/api/metadata/graphql"

    query = get_datasource_query(datasource_luid)

    payload = json.dumps({
        "query": query,
        "variables": {}
    })

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-Tableau-Auth': api_key
    }

    response = requests.post(full_url, headers=headers, data=payload)
    response.raise_for_status()  # Raise an exception for bad status codes

    dictionary = response.json()

    return dictionary['data']
