# This is the document to generate pivots for different clusters. You can customize your own way of the pivots you wish to generate.
# The current code is an example to generate random pivots (center of the cluster). 
# The code utilize mongoDB Atlas, please update the db information with your own for testing.

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
    # if i == 0:
    #     matrix = 5 * np.random.rand(rows, columns)
    # elif i == 1:
    #     matrix = np.zeros((rows, columns))
    #     matrix[:, 0] = 5 * np.random.rand(rows)
    # elif i == 2:
    #     matrix = np.zeros((rows, columns))
    #     matrix[:, 1] = 5 * np.random.rand(rows)
    #     matrix[:, 3] = 5 * np.random.rand(rows)
    #     matrix[:, 5] = 5 * np.random.rand(rows)
    # elif i == 3:
    #     matrix = 2.5 + np.random.rand(rows, columns) * (3.5 - 2.5)
    # else:
    #     matrix = 4.5 + np.random.rand(rows, columns) * (5.0 - 4.5)
    matrix = matrix = 5 * np.random.rand(rows, columns)
    matrix_list = matrix.tolist()
    collection.find_one_and_update(
        {'user_id': 'total'},
        {'$set': {
            f'cluster_data.cluster_{i}': matrix_list,
        }},
        return_document=True, # Return the updated document
        upsert=True           # Create a new document if one doesn't exist
    )

# Some sample code for references only:----------------------------------------------
# # matrix = np.zeros((rows, columns))
# # matrix[:, 0] = 5 * np.random.rand(rows)

# # matrix = np.zeros((rows, columns))
# # matrix[:, 1] = 5 * np.random.rand(rows)
# # matrix[:, 3] = 5 * np.random.rand(rows)
# # matrix[:, 5] = 5 * np.random.rand(rows)

# # matrix = 2.5 + np.random.rand(rows, columns) * (3.5 - 2.5)
#     # else:
# matrix = 4.5 + np.random.rand(rows, columns) * (5.0 - 4.5)
    
# matrix_list = matrix.tolist()
# collection.find_one_and_update(
#     {'user_id': 'total'},
#     {'$set': {
#         f'cluster_data.cluster_4': matrix_list,
#     }},
#     return_document=True, # Return the updated document
#     upsert=True           # Create a new document if one doesn't exist
# )


# Please remeber close connection with the database:
db_client.close()