from typing import Dict, Any, Optional
import aiohttp
import json


async def http_get(endpoint: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Reusable asynchronous HTTP GET requests.

    Args:
        endpoint (str): The URL to send the GET request to.
        headers (Optional[Dict[str, str]]): Optional headers to include in the request.

    Returns:
        Dict[str, Any]: A dictionary containing the status code and either the JSON response or response text.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(endpoint, headers=headers) as response:
            response_data = await response.json() if response.status == 200 else await response.text()
            return {
                'status': response.status,
                'data': response_data
            }


async def http_post(endpoint: str, headers: Optional[Dict[str, str]] = None, payload: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Reusable asynchronous HTTP POST requests.

    Args:
        endpoint (str): The URL to send the POST request to.
        headers (Optional[Dict[str, str]]): Optional headers to include in the request.
        payload (Optional[Dict[str, Any]]): The data to send in the body of the request.

    Returns:
        Dict[str, Any]: A dictionary containing the status code and either the JSON response or response text.
    """
    async with aiohttp.ClientSession() as session:
        async with session.post(endpoint, headers=headers, json=payload) as response:
            response_data = await response.json() if response.status == 200 else await response.text()
            return {
                'status': response.status,
                'data': response_data
            }


def json_to_markdown_table(json_data):
    if isinstance(json_data, str):
        json_data = json.loads(json_data)
    # Check if the JSON data is a list and not empty
    if not isinstance(json_data, list) or not json_data:
        raise ValueError(f"Invalid JSON data, you may have an error or if the array is empty then it was not possible to resolve the query your wrote: {json_data}")

    headers = json_data[0].keys()

    markdown_table = "| " + " | ".join(headers) + " |\n"
    markdown_table += "| " + " | ".join(['---'] * len(headers)) + " |\n"

    for entry in json_data:
        row = "| " + " | ".join(str(entry[header]) for header in headers) + " |"
        markdown_table += row + "\n"

    return markdown_table
