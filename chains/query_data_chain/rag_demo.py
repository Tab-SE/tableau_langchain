from modules import graphql
import chromadb
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
import os
load_dotenv()
import chromadb.utils.embedding_functions as embedding_functions

openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def get_embedding_openai(text, model="text-embedding-3-small"):
   text = text.replace("\n", " ")
   return openai_client.embeddings.create(input = [text], model=model).data[0].embedding


openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                api_key=os.getenv('OPENAI_API_KEY'),
                model_name="text-embedding-3-small"
            )

def convert_to_string(value):
    if isinstance(value, dict):
        return str(value)
    elif isinstance(value, list):
        return ', '.join(map(str, value))
    else:
        return str(value)

server, auth = graphql.get_tableau_client()
datasources = graphql.fetch_datasources(server, auth)

# Initialise Chroma
chroma_client = chromadb.PersistentClient(path="data")
collection_name = 'tableau_datasource_RAG_search'
collection = chroma_client.get_collection(name=collection_name, embedding_function=openai_ef)

if collection:
    print("Collection exists.")
    # Run your series of code here
else:
    print("Collection does not exist. Creating collection...")
    documents = []
    embeddings = []
    ids = []
    metadatas = []

    for datasource in datasources:
        # Extract the text to embed
        text_to_embed = datasource['dashboard_overview']

        # Extract the unique identifier
        unique_id = datasource['id']

        # Prepare metadata (exclude 'dashboard_overview' and 'id')
        metadata = {k: v for k, v in datasource.items() if k not in ['dashboard_overview', 'id']}

        # Remove any nested data structures from metadata (e.g., lists, dicts)
        metadata = {k: convert_to_string(v) for k, v in metadata.items() if isinstance(v, (str, int, float, bool, dict, list))}

        documents.append(text_to_embed)
        ids.append(unique_id)
        
        metadatas.append(metadata)
    
    # Create vector db with openai embedding
    collection = chroma_client.get_or_create_collection(name=collection_name, embedding_function=openai_ef)

    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )

# to Reset vector db
# # chroma_client.delete_collection(name=collection_name)
# collection = chroma_client.get_or_create_collection(name=collection_name, embedding_function=openai_ef)

results = collection.query(
    query_texts=["Why is my dashboard slow?"], 
    n_results=2 
)

metadatas = results['metadatas']
distances = results['distances']

# Initialize an empty list to store extracted data
extracted_data = []

for meta_list, dist_list in zip(metadatas, distances):
    for metadata, distance in zip(meta_list, dist_list):
        name = metadata.get('name', 'N/A')
        uri = metadata.get('uri', 'N/A')
        luid = metadata.get('luid', 'N/A')
        isCertified = metadata.get('isCertified', 'N/A')
        updatedAt = metadata.get('updatedAt', 'N/A')
        
        # Append the extracted data to the list, including 'distance'
        extracted_data.append({
            'name': name,
            'uri': uri,
            'luid': luid,
            'isCertified': isCertified,
            'updatedAt': updatedAt,
            'distance': distance
        })


for item in extracted_data:
    print(f"Name: {item['name']}")
    print(f"URI: {item['uri']}")
    print(f"LUID: {item['luid']}")
    print(f"Certified?: {item['isCertified']}")
    print(f"Last Update: {item['updatedAt']}")
    print(f"Vector distance: {item['distance']}")
    print("-" * 40)



