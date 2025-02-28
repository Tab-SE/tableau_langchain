from typing import Dict, Any
import requests


def query_vds(api_key: str, datasource_luid: str, url: str, query: Dict[str, Any]) -> Dict[str, Any]:
    full_url = f"{url}/api/v1/vizql-data-service/query-datasource"

    payload = {
        "datasource": {
            "datasourceLuid": datasource_luid
        },
        "query": query
    }

    headers = {
        'X-Tableau-Auth': api_key,
        'Content-Type': 'application/json'
    }

    response = requests.post(full_url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()
    else:
        error_message = (
            f"Failed to query data source via Tableau VizQL Data Service. "
            f"Status code: {response.status_code}. Response: {response.text}"
        )
        raise RuntimeError(error_message)


def query_vds_metadata(api_key: str, datasource_luid: str, url: str) -> Dict[str, Any]:
    full_url = f"{url}/api/v1/vizql-data-service/read-metadata"

    payload = {
        "datasource": {
            "datasourceLuid": datasource_luid
        }
    }

    headers = {
        'X-Tableau-Auth': api_key,
        'Content-Type': 'application/json'
    }

    response = requests.post(full_url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()
    else:
        error_message = (
            f"Failed to obtain data source metadata from VizQL Data Service. "
            f"Status code: {response.status_code}. Response: {response.text}"
        )
        raise RuntimeError(error_message)
