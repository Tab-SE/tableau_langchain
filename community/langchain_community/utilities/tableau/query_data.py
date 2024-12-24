import requests, json, re

# define the headless BI query template
def query_vds(**kwargs):
    """
    Queries Tableau's VizQL Data Service with a parameterized query in the payload
    Returns data sets to the end user as well as metadata used before querying
    """
    api_key = kwargs['api_key']
    datasource_luid = kwargs['datasource_luid']
    url = kwargs['url'] + '/api/v1/vizql-data-service/query-datasource'
    query = kwargs['query']

    payload = json.dumps({
        "datasource": {
            "datasourceLuid": datasource_luid
        },
        "query": query
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
        print("Failed to query data source via Tableau VizQL Data Service. Status code:", response.status_code)
        print(response.text)

# sends request to VizQL Data Service with payload written by Agent
def get_headlessbi_data(**kwargs):
    """
    Returns a dictionary containing a data consisting of formatted markdown and a query plan
    describing the reasoning and steps the model performed in order to generate the query payload
    """
    agent_response = get_payload(kwargs['payload'])
    vds_payload = agent_response["payload"]
    query_plan = agent_response["query_plan"]

    # when data is available return it and the reasoning behind the query
    if vds_payload:
        headlessbi_data = query_vds(
            api_key = kwargs['api_key'],
            datasource_luid = kwargs['datasource_luid'],
            url = kwargs['url'],
            query = vds_payload
        )

        # Convert to JSON string
        markdown_table = json_to_markdown(headlessbi_data)

        # response includes markdown table with data + query plan
        return {
            "query_plan": query_plan,
            "data": markdown_table
        }
    # when the LLM cannot generate a query, the reasoning will explain why
    else:
        return {
            "query_plan": query_plan,
            "data": None
        }

# separates the written payload from the Agent's reasoning
def get_payload(output):
    """
    Extracts the LLM generated payload to query Tableau VizQL Data Service on behalf of
    the end user. It also separates the behavioral reasoning generated by the model, inserting
    both generations into individual dictionary keys
    """

    # LLM reasoning
    query_plan = output.split('JSON_payload')[0]

    # parse LLM output and query headless BI
    parsed_output = output.split('JSON_payload')[1]

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

# convert JSON responses to formatted markdown
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
    url = kwargs['url'] + '/api/v1/vizql-data-service/read-metadata'

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

# extract column or field values
def get_values(**kwargs):
    """
    Returns the available members or column values of a data source field
    """

    column_values = {'fields': [{'fieldCaption': kwargs['caption']}]}
    output = query_vds(
        api_key = kwargs['api_key'],
        datasource_luid = kwargs['datasource_luid'],
        url = kwargs['url'],
        query=column_values
    )
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
    datasource_metadata = query_metadata(
        api_key=api_key,
        url=url,
        datasource_luid=datasource_luid
    )

    counter = 0

    for field in datasource_metadata:
        if counter == 3:
            print("\nAgent:")
        elif counter == 6:
            print("Ok, first I'll get as much metadata as I can about this data source...")
        elif counter == 9:
            print("I'll index field values so I can filter the data according to your specifications...")
        del field['fieldName']
        del field['logicalTableId']
        if field['dataType'] == 'STRING':
            string_values=get_values(
                api_key=api_key,
                url=url,
                datasource_luid=datasource_luid,
                caption=field['fieldCaption']
            )
            field['sampleValues'] = string_values
        counter+=1
        if counter == len(datasource_metadata) - 1:
            print("I have the necessary metadata and will write an API query for you")

    # add the datasource metadata of the connected datasource to the system prompt
    prompt['data_model'] = datasource_metadata

    return json.dumps(prompt)
