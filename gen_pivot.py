import numpy as np
import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Define connection_string of mongoDB:
load_dotenv()
DB_CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING")
DB_NAME = os.getenv("DB_NAME")
CLUSTER_SIZE = 5   # change cluster size
rows = 10          # number of suggestions
columns = 6        # number of contexts

db_client = MongoClient(DB_CONNECTION_STRING)
db = db_client[DB_NAME]
collection = db['total_data']
user_documents = collection.find_one({'user_id': 'total'})

for i in range(CLUSTER_SIZE):
    matrix = 5 * np.random.rand(rows, columns)
    matrix_list = matrix.tolist()
    collection.find_one_and_update(
        {'user_id': 'total'},
        {'$set': {
            f'cluster_data.cluster_{i}': matrix_list,
        }},
        return_document=True, # Return the updated document
        upsert=True           # Create a new document if one doesn't exist
    )


db_client.close()