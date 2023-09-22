# This is the MAB class object implemented with the Upper Confidence Bound Algorithm.
import os
import yaml
import numpy as np
from ContextualMAB import ContextualMAB

# Read from yaml file, get data:
with open("configuration.yaml", "r") as yaml_file:
   data = yaml.safe_load(yaml_file)

reco_size = data["recommendation_size"]
contexts = data["contexts"]
suggestions = data["suggestions"]
sugg_dict = data["sugg_dict"]
avoid_indices = data["avoid_indices"]

# check to say if we need modify the non-selected suggestions:
modify_non_selected = data["modify_non_selected"]
threshold_num = data["threshold_num"]
auxiliary_rewards = data["auxiliary_rewards"]

# Name file paths:
parent_directory = os.path.join(os.getcwd(), '..')
user_activity_folder_path = os.path.join(parent_directory, data["user_activity_folder_name"])
mab_data_folder_path = os.path.join(parent_directory, data["mab_data_folder_name"])
image_folder_path = os.path.join(parent_directory, data["image_folder_name"])

history_data_file_name = data["history_mab_data_file_name"]
history_activity_file_name = data["history_activity_file_name"]

# If folder not there, create it:
if not os.path.exists(user_activity_folder_path):
   os.mkdir(user_activity_folder_path)
if not os.path.exists(mab_data_folder_path):
   os.mkdir(mab_data_folder_path)
if not os.path.exists(image_folder_path):
   os.mkdir(image_folder_path)

class MABInstance:
   def __init__(self, user_hash, personalization, platform):
      self.user_hash = user_hash
      self.personalization = personalization
      self.platform = platform
      
      # define platform data and activity folders:
      platform_mab_folder_path = os.path.join(mab_data_folder_path, platform)
      platform_activity_folder_path = os.path.join(user_activity_folder_path, platform)
      if not os.path.exists(platform_mab_folder_path):
         os.mkdir(platform_mab_folder_path)
      if not os.path.exists(platform_activity_folder_path):
         os.mkdir(platform_activity_folder_path)
 
      # mab data files:
      self.history_data_file = os.path.join(mab_data_folder_path, history_data_file_name)
      self.user_data_file = os.path.join(platform_mab_folder_path, f"{self.user_hash}_mab.txt")
      
      # activity log files:
      self.history_activity_file = os.path.join(user_activity_folder_path, history_activity_file_name)
      self.user_activity_file = os.path.join(platform_activity_folder_path, f"{self.user_hash}_activity.json")

      self.image_folder_path = image_folder_path
      
      if os.path.exists(self.history_data_file):
         if modify_non_selected:
            self.general_mab_instance = ContextualMAB(len(suggestions), len(contexts), 2, self.history_data_file, threshold_num, auxiliary_rewards)
         else:
            self.general_mab_instance = ContextualMAB(len(suggestions), len(contexts), 2, self.history_data_file)
      else:
         if modify_non_selected:
            self.general_mab_instance = ContextualMAB(len(suggestions), len(contexts), 2, threshold_num=threshold_num, non_selected_rewards=auxiliary_rewards)
         else:
            self.general_mab_instance = ContextualMAB(len(suggestions), len(contexts), 2)
      
      if os.path.exists(self.user_data_file):
         if modify_non_selected:
            self.user_mab_instance = ContextualMAB(len(suggestions), len(contexts), 2, self.user_data_file, threshold_num, auxiliary_rewards)
         else:
            self.user_mab_instance = ContextualMAB(len(suggestions), len(contexts), 2, self.user_data_file)
      else:
         if modify_non_selected:
            self.user_mab_instance = ContextualMAB(len(suggestions), len(contexts), 2, threshold_num=threshold_num, non_selected_rewards=auxiliary_rewards)
         else:
            self.user_mab_instance = ContextualMAB(len(suggestions), len(contexts), 2)

   # Returns the contexts:
   def get_contexts(self):
      return contexts

   # Returns the suggestions:
   def get_suggestions(self):
      return suggestions

   # Returns suggestion based on given context:
   def make_recommendation(self, context_idx, prev_sugg_indices=None):
      ctx_avoid_indices = avoid_indices[context_idx]
      if prev_sugg_indices is not None:
         ctx_avoid_indices = np.unique(np.concatenate((ctx_avoid_indices, prev_sugg_indices)).astype(int))

      if self.personalization:
         sugg_indices = self.user_mab_instance.recommend(reco_size, context_idx, self.user_mab_instance.is_first_time(context_idx, reco_size), ctx_avoid_indices)
      else:
         sugg_indices = self.general_mab_instance.recommend(reco_size, context_idx, self.general_mab_instance.is_first_time(context_idx, reco_size), ctx_avoid_indices)
      
      sugg_list = [suggestions[idx] for idx in sugg_indices]
      
      return sugg_list

   # Returns the suggestion index:
   def get_suggestion_index(self, suggestion):
      return suggestions.index(suggestion)

   def get_suggestion_description(self, suggestion_idx):
      suggestion = suggestions[suggestion_idx]
      return sugg_dict[suggestion]['description']

   # Return image path:
   def get_suggestion_Image(self, suggestion_idx):
      suggestion = suggestions[suggestion_idx]
      return os.path.join(self.image_folder_path, sugg_dict[suggestion]['img_file_name'])
   
   # Update mab scores: 
   # suggestion_idx = -1 & feedback = -1 if all suggestions are not selected by the user (user doesn't like all of them):
   def update_mab_file(self, context_idx, suggestion_idx, feedback, suggestion_idx_list):
      # re-create mab instances due to concurrency to avoid any issues:
      if os.path.exists(self.history_data_file):
         if modify_non_selected:
            self.general_mab_instance = ContextualMAB(len(suggestions), len(contexts), 2, self.history_data_file, threshold_num, auxiliary_rewards)
         else:
            self.general_mab_instance = ContextualMAB(len(suggestions), len(contexts), 2, self.history_data_file)
      if os.path.exists(self.user_data_file):
         if modify_non_selected:
            self.user_mab_instance = ContextualMAB(len(suggestions), len(contexts), 2, self.user_data_file, threshold_num, auxiliary_rewards)
         else:
            self.user_mab_instance = ContextualMAB(len(suggestions), len(contexts), 2, self.user_data_file)

      if modify_non_selected:
         for i in range(len(suggestion_idx_list)):
            if suggestion_idx_list[i] == suggestion_idx:
               self.general_mab_instance.update(feedback, suggestion_idx, context_idx, self.history_data_file)
               self.user_mab_instance.update(feedback, suggestion_idx, context_idx, self.user_data_file)
            else:
               self.general_mab_instance.update(feedback, suggestion_idx_list[i], context_idx, self.history_data_file, False)
               self.user_mab_instance.update(feedback, suggestion_idx_list[i], context_idx, self.user_data_file, False)
      else:
         if suggestion_idx != -1 and feedback != -1:
            self.general_mab_instance.update(feedback, suggestion_idx, context_idx, self.history_data_file)
            self.user_mab_instance.update(feedback, suggestion_idx, context_idx, self.user_data_file)
         
   # Update activity log:
   def update_activity_log(self, curr_time, context_idx, suggestion_idx, feedback):
      # format json entry
      activity_entry = {
         "timestamp": curr_time,
         "platform": self.platform,
         "user_hash": self.user_hash,
         "context": contexts[context_idx],
         "recommendation": suggestions[suggestion_idx],
         "feedback": feedback
      }
      self.general_mab_instance.update_activity_log(self.history_activity_file, activity_entry)
      self.user_mab_instance.update_activity_log(self.user_activity_file, activity_entry)