import os, requests, json, re

# define the headless BI query template
def query_vds(query):
    """
    Queries Tableau's VizQL Data Service with a parameterized query in the payload
    Returns data sets to the end user as well as metadata used before querying
    """
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
        print("Failed to query data source via Tableau VizQL Data Service. Status code:", response.status_code)
        print(response.text)

# sends request to VizQL Data Service with payload written by Agent
def get_headlessbi_data(message):
    """
    Returns a dictionary containing a data consisting of formatted markdown and a query plan
    describing the reasoning and steps the model performed in order to generate the query payload
    """
    payload = get_payload(message)
    # when data is available return it and the reasoning behind the query
    if payload["payload"]:
        headlessbi_data = query_vds(payload["payload"])

        # Convert to JSON string
        markdown_table = json_to_markdown(headlessbi_data)

        # response includes markdown table with data + query plan
        return {
            "query_plan": payload["query_plan"],
            "data": markdown_table
        }
    # when the LLM cannot generate a query, the reasoning will explain why
    else:
        return {
            "query_plan": payload["query_plan"],
        }


def get_payload(output):
    """
    Extracts the LLM generated payload to query Tableau VizQL Data Service on behalf of
    the end user. It also separates the behavioral reasoning generated by the model, inserting
    both generations into individual dictionary keys
    """
    content = output.content

    print('*** Query Generation ***\n', content)

    # LLM reasoning
    query_plan = content.split('JSON_payload')[0]
    # print('*** reasoning ***', reasoning)

    # parse LLM output and query headless BI
    parsed_output = content.split('JSON_payload')[1]
    # print('*** parsed_output ***', parsed_output)

    match = re.search(r'{.*}', parsed_output, re.DOTALL)
    if match:
        json_string = match.group(0)
        payload = json.loads(json_string)

        return {
            "query_plan": query_plan,
            "payload": payload
        }
    else:
        # for when no payload is possible to generate
        return {
            "query_plan": query_plan
        }


def json_to_markdown(json_data):
    """
    Parses a JSON response from Tableau's VizQL Data Service into formatted markdown
    """
    # Parse the JSON data if it's a string
    if isinstance(json_data, str):
        json_data = json.loads(json_data)

    # Check if the JSON data is a list and not empty
    if not isinstance(json_data, list) or not json_data:
        return "Invalid JSON data"

    # Extract headers from the first dictionary
    headers = json_data[0].keys()

    # Create the Markdown table header
    markdown_table = "| " + " | ".join(headers) + " |\n"
    markdown_table += "| " + " | ".join(['---'] * len(headers)) + " |\n"

    # Add each row to the Markdown table
    for entry in json_data:
        row = "| " + " | ".join(str(entry[header]) for header in headers) + " |"
        markdown_table += row + "\n"

    return markdown_table


# request metadata of declared datasource (READ_METADATA)
def query_metadata(**kwargs):
    """
    Gets metadata from the VizQL Data Service endpoint for the specified data source
    """
    api_key = kwargs['api_key']
    datasource_luid = kwargs['datasource_luid']
    url = kwargs['url']

    payload = json.dumps({
        "datasource": {
            "datasourceLuid": datasource_luid
        },
    })

    headers = {
        'X-Tableau-Auth': api_key,
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        data = response.json()['data']
        return data
    else:
        print("Failed to obtain data source metadata from VizQL Data Service. Status code:", response.status_code)
        print(response.text)


def get_values(column_name):
    """
    Returns the available members or column values of a data source field
    """
    column_values = {'columns': [{'columnName': column_name}]}
    output = query_vds(column_values)
    if output is None:
        return None
    sample_values = [list(item.values())[0] for item in output][:4]
    return sample_values


# obtains datasource metadata to augment the tool prompt
def augment_datasource_metadata(**kwargs):
    """
    Enhances the provided prompt (expecting a key called "data_model") with metadata
    describing a Tableau data source such that an Agent can correctly write queries to meet
    the user's needs with regards to fields, filters and calculations
    """
    api_key = kwargs['api_key']
    url = kwargs['url']
    datasource_luid = kwargs['datasource_luid']
    prompt = kwargs['prompt']

    # get metadata from VizQL Data Service endpoint
    datasource_metadata = query_metadata(api_key, url, datasource_luid)

    data_model = []

    for field in datasource_metadata:
        column_dict = {}
        del field['objectGraphId']
        column_dict['caption'] = field['caption']
        column_dict['colName'] = field['columnName']
        if field['dataType'] == 'STRING':
            # get available members or column values of a data source field
            string_values = get_values(field['columnName'])
            column_dict['sampleValues'] = string_values
        else:
            column_dict['sampleValues'] = ""
        data_model.append(column_dict)

    # add the datasource metadata of the connected datasource to the system prompt
    prompt['data_model'] = data_model

    return json.dumps(prompt, indent=2)