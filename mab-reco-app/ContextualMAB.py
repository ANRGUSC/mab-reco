# This is the MAB class object implemented with the Upper Confidence Bound Algorithm.

import numpy as np
import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Define connection_string of mongoDB:
load_dotenv()
DB_CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING")
DB_NAME = os.getenv("DB_NAME")

class ContextualMAB:
   # By default, we won't modify the non-selected suggestions after the "threshold_num" total selections, just omit the last two parameters.
   # The "history_data_file" parameter is only used if there are historical data to read and build this mab instance.
   def __init__(self, num_suggestions, num_contexts, exploration_param, platform, user_hash, threshold_num=None, non_selected_rewards=None):
      self.num_suggestions = num_suggestions
      self.num_contexts = num_contexts
      self.exploration_param = exploration_param
      self.platform = platform
      self.user_hash = user_hash
      self.threshold_num = threshold_num  # start doing so when we reach the threshold data points
      self.non_selected_rewards = non_selected_rewards
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
      else:
         self.mab_data = self.user_documents.get('mab_data', {})
         self.rewards = np.array(self.mab_data.get('rewards', np.zeros((num_suggestions, num_contexts))))
         self.selections = np.array(self.mab_data.get('selections', np.zeros((num_suggestions, num_contexts))))
         self.mab_scores = np.array(self.mab_data.get('mab_scores', np.full((num_suggestions, num_contexts), float('inf'))), dtype=object)
         self.total_selections = self.mab_data.get('total_selections', 0)

   # Recommend the top rec_size suggestions based on given context:
   def recommend(self, rec_size, context_index, first_time, avoid_indices=None):
      # records all mab scores for the given context for different suggestions
      context_mab_scores = self.mab_scores[:, context_index]
      if first_time:
         if avoid_indices is None or len(avoid_indices) == 0:
            if len(context_mab_scores) < rec_size:
               indices = np.arange(len(context_mab_scores))
               return np.random.permutation(indices)
            else:
               return np.random.choice(len(context_mab_scores), size=rec_size, replace=False)
         else:
            valid_indices = [i for i in range(len(context_mab_scores)) if i not in avoid_indices]
            if len(valid_indices) < rec_size:
               return np.random.permutation(valid_indices)
            else:
               return np.random.choice(valid_indices, size=rec_size, replace=False)
      else:
         if avoid_indices is None or len(avoid_indices) == 0:
            return np.argsort(context_mab_scores)[-rec_size:][::-1]
         else:
            sorted_indices = np.argsort(context_mab_scores)
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

   # check the current data and see if we can consider the pick is the first time:
   def is_first_time(self, context_index, reco_size):
      context_selections = self.selections[:, context_index]
      if self.total_selections == 0 or np.sum(context_selections) < reco_size:
         return True
      else:
         return False
   
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

   # close the database client once everything is done:
   def close_db(self):
      self.db_client.close()