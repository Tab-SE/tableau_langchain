import os, requests, json
from modules.headless import query
from modules.prompts import nlq_to_vds

import logging

# Set up the logger for this module
logger = logging.getLogger(__name__)

# request metadata of declared datasource (READ_METADATA)
def read():
    url = os.getenv('READ_METADATA')
    payload = json.dumps({
        "connection": {
            "tableauServerName": os.getenv('TABLEAU_DOMAIN'),
            "siteId": os.getenv('SITE_NAME'),
            "datasource": os.getenv('DATA_SOURCE')
        },
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

def get_values(column_name):
     column_values = {'columns': [{'columnName': column_name}]}
     output = query(column_values)
     if output is None:
        return None
     sample_values = [list(item.values())[0] for item in output][:4]
     return sample_values

def instantiate_prompt():
    datasource_metadata = read()

    data_model = []

    for field in datasource_metadata:
        column_dict = {}
        del field['objectGraphId']
        column_dict['caption'] = field['caption']
        column_dict['colName'] = field['columnName']
        if field['dataType'] == 'STRING':
            string_values = get_values(field['columnName'])
            column_dict['sampleValues'] = string_values
        else:
            column_dict['sampleValues'] = ""
        data_model.append(column_dict)

    # add the datasource metadata of the connected datasource to the system prompt
    nlq_to_vds.prompt['data_model'] = data_model
    return json.dumps(nlq_to_vds.prompt, indent=2)
