import os
from dotenv import load_dotenv

from experimental.demos.server_vector_db_utils import (
    query_tableau_vector_db
)

# # Load environment variables (Tableau creds, OpenAI API key, etc.)
load_dotenv()

# # Read Tableau authentication config from environment
# tableau_server   = 'https://' + os.getenv('TABLEAU_SRV_DOMAIN')   
# tableau_site     = os.getenv('SRV_SITE_NAME')        
# tableau_user     = os.getenv('TABLEAU_SRV_USER')     

# # Credentials for generating auth token via connnected app
# tableau_jwt_client_id    = os.getenv('TABLEAU_SRV_JWT_CLIENT_ID')
# tableau_jwt_secret_id    = os.getenv('TABLEAU_SRV_JWT_SECRET_ID')
# tableau_jwt_secret = os.getenv('TABLEAU_SRV_JWT_SECRET')
# tableau_api_version  = os.getenv('TABLEAU_SRV_API') 

# DEFAULT_COLLECTION_NAME = f"{tableau_site}_tableau_datasource_vector_search"
# debug = False


# collection_name = f"{tableau_site}_tableau_datasource_vector_search"
# print(collection_name)

# # Simple query example
# query_text = "who won gold in olympic rowing?"
# results = query_tableau_vector_db(
#     query_text=query_text,
#     collection_name=collection_name,
#     n_results=10,
#     debug=False
# )

# print(results)


# from modules import graphql, vectorstore
from flask import Flask, request, jsonify, render_template, send_file
import json 
import os
from experimental.utilities.setup_local_vector_db import query_tableau_vector_db
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

tableau_site = os.getenv('SITE_NAME')
collection_name = f"{tableau_site}_tableau_datasource_vector_search"

# Initialize Flask app with correct template folder
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                           'ui_templates')

static_dir = os.path.join(template_dir, 'static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# Route to display the search form
@app.route('/', methods=['GET'])
def index():
    return render_template('search.html')

# Route to handle search queries
@app.route('/search', methods=['POST'])
def search():
    # Get the user's query from the form
    user_input = request.form.get('query')
    if not user_input:
        return jsonify({"error": "No query provided"}), 400

    # Use the new query_tableau_vector_db function
    results = query_tableau_vector_db(
        query_text=user_input,
        collection_name=collection_name,
        n_results=10,
        debug=False
    )

    # Add some debug information
    extracted_data = []

    num_items = len(results['luid'])

    # Iterate over the indices of the lists
    for i in range(num_items):
        # Get the metadata for the current index
        metadata = results['metadatas'][i]
        
        # Append a dictionary with the desired fields
        extracted_data.append({
            'name': metadata.get('name', 'N/A'),
            'has_active_warning': metadata.get('has_active_warning', 'N/A'),
            'dashboard_luid': results['luid'][i],
            'is_certified': metadata.get('is_certified', 'N/A'),
            'project_name': metadata.get('project_name', 'N/A'),
            'distance': results['distances'][i]
        })

    # Render the results template
    return render_template('results.html', results=extracted_data, query=user_input)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
