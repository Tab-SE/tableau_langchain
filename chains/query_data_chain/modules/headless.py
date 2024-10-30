import os, requests, json, logging

# Set up the logger
logger = logging.getLogger(__name__)

# define the headless BI query template
def query(query):
    url = os.getenv('HEADLESSBI_URL')
    payload = json.dumps({
        "connection": {
            "tableauServerName": os.getenv('TABLEAU_DOMAIN'),
            "siteId": os.getenv('SITE_NAME'),
            "datasource": os.getenv('DATA_SOURCE')
        },
        "query": query
    })

    headers = {
    'Credential-Key': os.getenv('PAT_NAME'),
    'Credential-value': os.getenv('PAT_SECRET'),
    'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        data = response.json()['data']
        return data
    else:
        logger.info("Failed to fetch data from the API. Status code:", response.status_code)
        logger.info(response.text)
