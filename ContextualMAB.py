# This is the MAB class object implemented with the Upper Confidence Bound Algorithm.

import numpy as np
import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Define connection_string of mongoDB:
load_dotenv()
DB_CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING")
DB_NAME = os.getenv("DB_NAME")
CLUSTER_SIZE = 5
RATIO_DIFF = 0.1 # Bigger positive value implies more weight on the cluster data when making recommendations, note 'cluster_reco_ratio/mab_reco_ratio +/- RATIO_DIFF' should be in range [0.0, 1.0]

class ContextualMAB:
   # By default, we won't modify the non-selected suggestions after the "threshold_num" total selections, just omit the last two parameters.
   # The "history_data_file" parameter is only used if there are historical data to read and build this mab instance.
   def __init__(self, num_suggestions, num_contexts, exploration_param, platform, user_hash, 
                threshold_num=None, non_selected_rewards=None,
                enable_cluster=False, cluster_reco_ratio=None, mab_reco_ratio=None, 
                cluster_refresh_threshold=None, assign_cluster_num=None, recluster_threshold=None):
      self.num_suggestions = num_suggestions
      self.num_contexts = num_contexts
      self.exploration_param = exploration_param
      self.platform = platform
      self.user_hash = user_hash
      self.threshold_num = threshold_num  # start doing so when we reach the threshold data points
      self.non_selected_rewards = non_selected_rewards
      self.enable_cluster = enable_cluster
      self.cluster_reco_ratio = cluster_reco_ratio
      self.mab_reco_ratio = mab_reco_ratio
      self.cluster_refresh_threshold = cluster_refresh_threshold
      self.assign_cluster_num = assign_cluster_num
      self.recluster_threshold = recluster_threshold
      # declare database:
      self.db_client = MongoClient(DB_CONNECTION_STRING)
      self.db = self.db_client[DB_NAME]
      self.collection = self.db[self.platform]
      # read and initiate c-mab parameters:
      self.user_documents = self.collection.find_one({'user_id': self.user_hash})
      if self.user_documents is None:
         # rewards is a num_arms (rows) x num_contexts (columns) matrix:
         self.rewards = np.zeros((num_suggestions, num_contexts))
         # records how many combination is picked:
         self.selections = np.zeros((num_suggestions, num_contexts))
         # record mab_scores:
         self.mab_scores = np.full((num_suggestions, num_contexts), float('inf'))
         # records total number of selections so far
         self.total_selections = 0
         if self.platform != "total_data" and self.enable_cluster:
            self.pref_vector = np.zeros((num_suggestions, num_contexts))
      else:
         self.mab_data = self.user_documents.get('mab_data', {})
         self.rewards = np.array(self.mab_data.get('rewards', np.zeros((num_suggestions, num_contexts))))
         self.selections = np.array(self.mab_data.get('selections', np.zeros((num_suggestions, num_contexts))))
         self.mab_scores = np.array(self.mab_data.get('mab_scores', np.full((num_suggestions, num_contexts), float('inf'))), dtype=object)
         self.total_selections = self.mab_data.get('total_selections', 0)
         if self.platform != "total_data" and self.enable_cluster:
            self.user_cluster_data = self.user_documents.get('cluster_data', {})
            if self.total_selections >= self.assign_cluster_num:
               self.user_cluster_id = self.user_cluster_data.get('cluster_id', f'cluster_{np.random.randint(0, CLUSTER_SIZE)}')
            self.pref_vector = np.array(self.user_cluster_data.get('pref_vector', np.zeros((num_suggestions, num_contexts))))
            # check if the pref. vector is in the correct dimension:
            self.check_user_pref_vector()
      # get cluster info:
      if self.enable_cluster:
         self.cluster_collection = self.db['total_data']
         self.cluster_documents = self.cluster_collection.find_one({'user_id': 'total'})
         self.cluster_data = self.cluster_documents.get('cluster_data', {})
         # check if the cluster pref. vector is in the correct dimension:
         self.check_cluster_data()

   # modify user pref vector in case of dimension change:
   def check_user_pref_vector(self):
      curr_row, curr_column = self.pref_vector.shape
      if curr_row == self.num_suggestions and curr_column == self.num_contexts:
         return
      else:
         # expand or shrink rows:
         if curr_row < self.num_suggestions:
            extra_rows = np.zeros((self.num_suggestions - curr_row, curr_column))
            self.pref_vector = np.vstack((self.pref_vector, extra_rows))
         elif curr_row > self.num_suggestions:
            self.pref_vector = self.pref_vector[:self.num_suggestions, :]

         # expand or shrink columns:
         if curr_column < self.num_contexts:
            extra_cols = np.zeros((self.num_suggestions, self.num_contexts - curr_column))
            self.pref_vector = np.hstack((self.pref_vector, extra_cols))
         elif curr_column > self.num_contexts:
            self.pref_vector = self.pref_vector[:, :self.num_contexts]
   
   # modify cluster pref vectors in case of dimension change:
   def check_cluster_data(self):
      changed = False
      for i in range(CLUSTER_SIZE):
         curr_cluster_data = np.array(self.cluster_data.get(f'cluster_{i}', np.zeros((self.num_suggestions, self.num_contexts))))
         curr_row, curr_column = curr_cluster_data.shape
         if curr_row == self.num_suggestions and curr_column == self.num_contexts:
            continue
         else:
            changed = True
            # expand or shrink rows:
            if curr_row < self.num_suggestions:
               extra_rows = np.random.rand(self.num_suggestions - curr_row, curr_column) * 5
               curr_cluster_data = np.vstack((curr_cluster_data, extra_rows))
            elif curr_row > self.num_suggestions:
               curr_cluster_data = curr_cluster_data[:self.num_suggestions, :]

            # expand or shrink columns:
            if curr_column < self.num_contexts:
               extra_cols = np.random.rand(self.num_suggestions, self.num_contexts - curr_column) * 5
               curr_cluster_data = np.hstack((curr_cluster_data, extra_cols))
            elif curr_column > self.num_contexts:
               curr_cluster_data = curr_cluster_data[:, :self.num_contexts]

            # update this in database:
            curr_cluster_data_list = curr_cluster_data.tolist()
            self.cluster_collection.find_one_and_update(
               {'user_id': 'total'},
               {'$set': {
                     f'cluster_data.cluster_{i}': curr_cluster_data_list,
               }},
               return_document=True, # Return the updated document
               upsert=True           # Create a new document if one doesn't exist
            )
      # if changed any:
      if changed:
         self.cluster_data = self.cluster_documents.get('cluster_data', {})

   # Recommend the top rec_size suggestions based on given context:
   def recommend(self, rec_size, context_index, first_time, avoid_indices=None):
      # records all mab scores for the given context for different suggestions
      context_mab_scores = self.mab_scores[:, context_index]
      # by default, we only use mab scores:
      reco_scores = context_mab_scores
      # if cluster feature is turned on:
      if self.platform != "total_data" and self.enable_cluster:
         context_pref_vector = self.pref_vector[:, context_index]
         # This implies the user is assigned to a cluster:
         if self.total_selections >= self.assign_cluster_num:
            user_cluster_data = np.array(self.cluster_data.get(self.user_cluster_id, np.zeros((self.num_suggestions, self.num_contexts))))
            context_user_cluster_data = user_cluster_data[:, context_index]
            reco_scores = (self.mab_reco_ratio - RATIO_DIFF) * context_mab_scores + (self.cluster_reco_ratio + RATIO_DIFF) * context_user_cluster_data
         else:
            reco_scores = self.mab_reco_ratio * context_mab_scores + self.cluster_reco_ratio * context_pref_vector

      # make recommendation based on the scores:
      if first_time:
         if avoid_indices is None or len(avoid_indices) == 0:
            if len(reco_scores) < rec_size:
               indices = np.arange(len(reco_scores))
               return np.random.permutation(indices)
            else:
               return np.random.choice(len(reco_scores), size=rec_size, replace=False)
         else:
            valid_indices = [i for i in range(len(reco_scores)) if i not in avoid_indices]
            if len(valid_indices) < rec_size:
               return np.random.permutation(valid_indices)
            else:
               return np.random.choice(valid_indices, size=rec_size, replace=False)
      else:
         if avoid_indices is None or len(avoid_indices) == 0:
            return np.argsort(reco_scores)[-rec_size:][::-1]
         else:
            sorted_indices = np.argsort(reco_scores)
            reco_indices = [idx for idx in sorted_indices if idx not in avoid_indices][-rec_size:][::-1]
            return reco_indices

   # Update mab score and reward for the given suggestion based on whether or not it is selected:
   def update(self, feedback_score, suggestion_index, context_index, selected=True):
      # if the given suggestion is selected by the user:
      if selected:
         # Suppose the feedback_score is in the range from 0 - 5: 0 implies no selection/unhelpful, where as 5 implies extremely helpful
         # update the selected suggestion with corresponding rewards
         self.rewards[suggestion_index][context_index] += feedback_score
         self.total_selections += 1
         self.selections[suggestion_index][context_index] += 1
         # update mab score:
         self.update_mab_score(suggestion_index, context_index)
         # update the mab data:
         self.update_mab_data()
         # if clustering feature is turned on:
         if self.enable_cluster:
            self.update_cluster_data(suggestion_index, context_index)
      else:
         if self.threshold_num is not None and self.non_selected_rewards is not None and self.total_selections > self.threshold_num:
            self.rewards[suggestion_index][context_index] += self.non_selected_rewards
            # only update mab if there is some selection count for this suggestion:
            if self.selections[suggestion_index][context_index] > 0:
               # update mab score:
               self.update_mab_score(suggestion_index, context_index)
            # update the mab data:
            self.update_mab_data()

   # Update the mab_score (exploitation + exploration):
   def update_mab_score(self, suggestion_index, context_index):
      # get exploitation & exploration score:
      exploitation_score = self.rewards[suggestion_index][context_index] / self.selections[suggestion_index][context_index]
      exploration_score = np.sqrt((self.exploration_param * np.log(self.total_selections)) / self.selections[suggestion_index][context_index])
      # update:
      self.mab_scores[suggestion_index][context_index] = exploitation_score + exploration_score
   
   # update mab data in database:
   def update_mab_data(self):
      rewards_list = self.rewards.tolist()
      mab_scores_list = self.mab_scores.tolist()
      selections_list = self.selections.tolist()
      self.collection.find_one_and_update(
         {'user_id': self.user_hash},
         {'$set': {
            'mab_data.rewards': rewards_list,
            'mab_data.selections': selections_list,
            'mab_data.mab_scores': mab_scores_list,
            'mab_data.total_selections': self.total_selections
         }},
         return_document=True, # Return the updated document
         upsert=True           # Create a new document if one doesn't exist
      )
   
   # Update cluster info:
   def update_cluster_data(self, suggestion_index, context_index):
      if self.platform != "total_data":
         # First, update user pref vector info:
         self.pref_vector[suggestion_index][context_index] = self.rewards[suggestion_index][context_index] / self.selections[suggestion_index][context_index]
         # Second, if the user needs to be assigned to a cluster or change cluster:
         if self.total_selections >= self.assign_cluster_num:
            self.update_user_cluster()
         # Third, update user cluster information and pref vector:
         pref_vector_list = self.pref_vector.tolist()
         self.collection.find_one_and_update(
            {'user_id': self.user_hash},
            {'$set': {
               'cluster_data.pref_vector': pref_vector_list
               # 'cluster_data.cluster_id': self.user_cluster_id
            }},
            return_document=True, # Return the updated document
            upsert=True           # Create a new document if one doesn't exist
         )
      # Finally, check if clusters need to be rearranged:
      if self.platform == "total_data" and self.total_selections >= self.recluster_threshold and self.total_selections % self.cluster_refresh_threshold == 0:
         self.refresh_cluster()

   # Update user with a cluster:
   def update_user_cluster(self):
      distances = []
      for i in range(CLUSTER_SIZE):
         distance = self.get_euclidean_dist(self.pref_vector, 
                                            self.cluster_data.get(f'cluster_{i}', 
                                                                  np.zeros((self.num_suggestions, self.num_contexts))))
         distances.append(distance)
      # get the index with shortest distance, update:
      target_cluster_index = np.argmin(distances)
      self.collection.find_one_and_update(
         {'user_id': self.user_hash},
         {'$set': {
            'cluster_data.cluster_id': f'cluster_{target_cluster_index}'
         }},
         return_document=True, # Return the updated document
         upsert=True           # Create a new document if one doesn't exist
      )

   # Re-clustering (k-mean clustering):
   def refresh_cluster(self):
      max_iteration_count = 1000
      tolerance = 1e-4
      # get current cluster pivot:
      pivots = []  # this is a list, no need to do tolist()
      for i in range(CLUSTER_SIZE):
         pivots.append(self.cluster_data.get(f'cluster_{i}', np.zeros((self.num_suggestions, self.num_contexts))))
      # get all users cluster data:
      user_cluster_data = []
      platforms = ["discord", "pwa", "telegram"]
      for platform in platforms:
         curr_plat = self.db[platform]
         plat_users = list(curr_plat.find({}, {"cluster_data.pref_vector": 1, "_id": 0}))
         for user in plat_users:
            user_pref_vector = user.get("cluster_data", {}).get("pref_vector")
            if user_pref_vector is not None:
               user_cluster_data.append(user_pref_vector)
      # iterate and recluster:
      for _ in range(max_iteration_count):
         # 1. Assign each user data point to the nearest cluster pivot
         labels = []
         for user_data in user_cluster_data:
            min_distance = float('inf')
            min_index = 0
            for i, pivot in enumerate(pivots):
               distance = self.get_euclidean_dist(np.array(user_data), np.array(pivot))
               if distance < min_distance:
                  min_distance = distance
                  min_index = i
            labels.append(min_index)

         # 2. Recompute the cluster pivots
         new_pivots = []
         for i in range(CLUSTER_SIZE):
            cluster_points = [user_cluster_data[j] for j, label in enumerate(labels) if label == i]
            if cluster_points:
               cluster_arrays = [np.array(point) for point in cluster_points]
               stacked_array = np.stack(cluster_arrays)
               pivot_mean = np.mean(stacked_array, axis=0)
               new_pivots.append(pivot_mean.tolist())
            else:
               new_pivots.append(pivots[i])

         # 3. Check for convergence
         pivot_diff = self.get_euclidean_dist(np.array(pivots), np.array(new_pivots))
         if pivot_diff < tolerance:
            break

         # 4. Update pivots:
         pivots = new_pivots

      # Update the cluster_data with the new pivots if needed
      for i in range(CLUSTER_SIZE):
         self.cluster_data[f'cluster_{i}'] = pivots[i]
         self.cluster_collection.find_one_and_update(
            {'user_id': 'total'},
            {'$set': {
               f'cluster_data.cluster_{i}': self.cluster_data[f'cluster_{i}'],
            }},
            return_document=True, # Return the updated document
            upsert=True           # Create a new document if one doesn't exist
         )

   # Compute euclidean distance between two 2D arrays:
   def get_euclidean_dist(self, arr1, arr2):
      return np.linalg.norm(arr1 - arr2)
   
   # update activity data in database:
   def update_activity(self, activity_entry):
      self.collection.find_one_and_update(
         {'user_id': self.user_hash},
         {'$push': {
            'activity_history': activity_entry
         }},
         return_document=True, # Return the updated document
         upsert=True           # Create a new document if one doesn't exist
      )
   
   # check the current data and see if we can consider the pick is the first time:
   def is_first_time(self, context_index, reco_size):
      context_selections = self.selections[:, context_index]
      if self.total_selections == 0 or np.sum(context_selections) < reco_size:
         return True
      else:
         return False

   # close the database client once everything is done:
   def close_db(self):
      self.db_client.close()