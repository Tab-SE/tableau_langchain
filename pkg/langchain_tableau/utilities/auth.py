
from typing import Dict, Any, List
import requests
import jwt
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from langchain_tableau.utilities.utils import http_post

def jwt_connected_app(
        tableau_domain: str,
        tableau_site: str,
        tableau_api: str,
        tableau_user: str,
        jwt_client_id: str,
        jwt_secret_id: str,
        jwt_secret: str,
        scopes: List[str],
) -> Dict[str, Any]:
    """
    Authenticates a user to Tableau using JSON Web Token (JWT) authentication.

    This function generates a JWT based on the provided credentials and uses it to authenticate
    a user with the Tableau Server or Tableau Online. The JWT is created with a specified expiration
    time and scopes, allowing for secure access to Tableau resources.

    Args:
        tableau_domain (str): The domain of the Tableau Server or Tableau Online instance.
        tableau_site (str): The content URL of the specific Tableau site to authenticate against.
        tableau_api (str): The version of the Tableau API to use for authentication.
        tableau_user (str): The username of the Tableau user to authenticate.
        jwt_client_id (str): The client ID used for generating the JWT.
        jwt_secret_id (str): The key ID associated with the JWT secret.
        jwt_secret (str): The secret key used to sign the JWT.
        scopes (List[str]): A list of scopes that define the permissions granted by the JWT.

    Returns:
        Dict[str, Any]: A dictionary containing the response from the Tableau authentication endpoint,
        typically including an API key or session that is valid for 2 hours and user information.
    """
    # Encode the payload and secret key to generate the JWT
    token = jwt.encode(
        {
        "iss": jwt_client_id,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        "jti": str(uuid4()),
        "aud": "tableau",
        "sub": tableau_user,
        "scp": scopes
        },
        jwt_secret,
        algorithm = "HS256",
        headers = {
        'kid': jwt_secret_id,
        'iss': jwt_client_id
        }
    )

    # authentication endpoint + request headers & payload
    endpoint = f"{tableau_domain}/api/{tableau_api}/auth/signin"

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    payload = {
        "credentials": {
        "jwt": token,
        "site": {
            "contentUrl": tableau_site,
        }
        }
    }

    response = requests.post(endpoint, headers=headers, json=payload)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        return response.json()
    else:
        error_message = (
            f"Failed to authenticate to the Tableau site. "
            f"Status code: {response.status_code}. Response: {response.text}"
        )
        raise RuntimeError(error_message)


async def jwt_connected_app_async(
        tableau_domain: str,
        tableau_site: str,
        tableau_api: str,
        tableau_user: str,
        jwt_client_id: str,
        jwt_secret_id: str,
        jwt_secret: str,
        scopes: List[str],
) -> Dict[str, Any]:
    """
    Authenticates a user to Tableau using JSON Web Token (JWT) authentication.

    This function generates a JWT based on the provided credentials and uses it to authenticate
    a user with the Tableau Server or Tableau Online. The JWT is created with a specified expiration
    time and scopes, allowing for secure access to Tableau resources.

    Args:
        tableau_domain (str): The domain of the Tableau Server or Tableau Online instance.
        tableau_site (str): The content URL of the specific Tableau site to authenticate against.
        tableau_api (str): The version of the Tableau API to use for authentication.
        tableau_user (str): The username of the Tableau user to authenticate.
        jwt_client_id (str): The client ID used for generating the JWT.
        jwt_secret_id (str): The key ID associated with the JWT secret.
        jwt_secret (str): The secret key used to sign the JWT.
        scopes (List[str]): A list of scopes that define the permissions granted by the JWT.

    Returns:
        Dict[str, Any]: A dictionary containing the response from the Tableau authentication endpoint,
        typically including an API key or session that is valid for 2 hours and user information.
    """
    # Encode the payload and secret key to generate the JWT
    token = jwt.encode(
        {
        "iss": jwt_client_id,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        "jti": str(uuid4()),
        "aud": "tableau",
        "sub": tableau_user,
        "scp": scopes
        },
        jwt_secret,
        algorithm = "HS256",
        headers = {
        'kid': jwt_secret_id,
        'iss': jwt_client_id
        }
    )

    # authentication endpoint + request headers & payload
    endpoint = f"{tableau_domain}/api/{tableau_api}/auth/signin"

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    payload = {
        "credentials": {
        "jwt": token,
        "site": {
            "contentUrl": tableau_site,
        }
        }
    }

    response = await http_post(endpoint=endpoint, headers=headers, payload=payload)
     # Check if the request was successful (status code 200)
    if response['status'] == 200:
        return response['data']
    else:
        error_message = (
            f"Failed to authenticate to the Tableau site. "
            f"Status code: {response['status']}. Response: {response['data']}"
        )
        raise RuntimeError(error_message)
