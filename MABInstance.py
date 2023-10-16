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

# cluster feature:
enable_cluster = data["enable_cluster"]
cluster_refresh_threshold = data["cluster_refresh_threshold"]
cluster_reco_ratio = data["cluster_reco_ratio"]    
mab_reco_ratio = data["mab_reco_ratio"]            
assign_cluster_num = data["assign_cluster_num"]  
recluster_threshold = data["recluster_threshold"]  

# Name file paths:
image_folder_path = os.path.join(os.getcwd(), data["image_folder_name"])
general_data_platform = data["general_data_platform"]
general_data_user_hash = data["general_data_user_hash"]

# If folder not there, create it:
if not os.path.exists(image_folder_path):
   os.mkdir(image_folder_path)

class MABInstance:
   def __init__(self, user_hash, personalization, platform):
      self.user_hash = user_hash
      self.personalization = personalization
      self.platform = platform
      self.image_folder_path = image_folder_path
      # initiate total and user mab instances:
      if modify_non_selected:
         self.general_mab_instance = ContextualMAB(len(suggestions), len(contexts), 2, 
                                                   general_data_platform, general_data_user_hash, threshold_num, auxiliary_rewards,
                                                   enable_cluster, cluster_reco_ratio, mab_reco_ratio, cluster_refresh_threshold, 
                                                   assign_cluster_num, recluster_threshold)
         self.user_mab_instance = ContextualMAB(len(suggestions), len(contexts), 2, 
                                                self.platform, self.user_hash, threshold_num, auxiliary_rewards,
                                                enable_cluster, cluster_reco_ratio, mab_reco_ratio, cluster_refresh_threshold, 
                                                assign_cluster_num, recluster_threshold)
      else:
         self.general_mab_instance = ContextualMAB(len(suggestions), len(contexts), 2, 
                                                   general_data_platform, general_data_user_hash,
                                                   enable_cluster=enable_cluster,
                                                   cluster_reco_ratio=cluster_reco_ratio, 
                                                   mab_reco_ratio=mab_reco_ratio, 
                                                   cluster_refresh_threshold=cluster_refresh_threshold, 
                                                   assign_cluster_num=assign_cluster_num,
                                                   recluster_threshold=recluster_threshold)
         self.user_mab_instance = ContextualMAB(len(suggestions), len(contexts), 2, 
                                                self.platform, self.user_hash,
                                                enable_cluster=enable_cluster,
                                                cluster_reco_ratio=cluster_reco_ratio, 
                                                mab_reco_ratio=mab_reco_ratio, 
                                                cluster_refresh_threshold=cluster_refresh_threshold, 
                                                assign_cluster_num=assign_cluster_num,
                                                recluster_threshold=recluster_threshold)

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
      # closes all former connections first:
      self.general_mab_instance.close_db()
      self.user_mab_instance.close_db()
      # re-create mab instances due to concurrency to avoid any issues:
      if modify_non_selected:
         self.general_mab_instance = ContextualMAB(len(suggestions), len(contexts), 2, 
                                                   general_data_platform, general_data_user_hash, threshold_num, auxiliary_rewards,
                                                   enable_cluster, cluster_reco_ratio, mab_reco_ratio, cluster_refresh_threshold, 
                                                   assign_cluster_num, recluster_threshold)
         self.user_mab_instance = ContextualMAB(len(suggestions), len(contexts), 2, 
                                                self.platform, self.user_hash, threshold_num, auxiliary_rewards,
                                                enable_cluster, cluster_reco_ratio, mab_reco_ratio, cluster_refresh_threshold, 
                                                assign_cluster_num, recluster_threshold)
      else:
         self.general_mab_instance = ContextualMAB(len(suggestions), len(contexts), 2, 
                                                   general_data_platform, general_data_user_hash,
                                                   enable_cluster=enable_cluster,
                                                   cluster_reco_ratio=cluster_reco_ratio, 
                                                   mab_reco_ratio=mab_reco_ratio, 
                                                   cluster_refresh_threshold=cluster_refresh_threshold, 
                                                   assign_cluster_num=assign_cluster_num,
                                                   recluster_threshold=recluster_threshold)
         self.user_mab_instance = ContextualMAB(len(suggestions), len(contexts), 2, 
                                                self.platform, self.user_hash,
                                                enable_cluster=enable_cluster,
                                                cluster_reco_ratio=cluster_reco_ratio, 
                                                mab_reco_ratio=mab_reco_ratio, 
                                                cluster_refresh_threshold=cluster_refresh_threshold, 
                                                assign_cluster_num=assign_cluster_num,
                                                recluster_threshold=recluster_threshold)
      # update accordingly:
      if modify_non_selected:
         for i in range(len(suggestion_idx_list)):
            if suggestion_idx_list[i] == suggestion_idx:
               self.general_mab_instance.update(feedback, suggestion_idx, context_idx)
               self.user_mab_instance.update(feedback, suggestion_idx, context_idx)
            else:
               self.general_mab_instance.update(feedback, suggestion_idx_list[i], context_idx, False)
               self.user_mab_instance.update(feedback, suggestion_idx_list[i], context_idx, False)
      else:
         if suggestion_idx != -1 and feedback != -1:
            self.general_mab_instance.update(feedback, suggestion_idx, context_idx)
            self.user_mab_instance.update(feedback, suggestion_idx, context_idx)

   # Update activity log:
   def update_activity_log(self, curr_time, context_idx, suggestion_idx, feedback):
      # format json entry
      general_activity_entry = {
         "user_id": self.user_hash,
         "platform": self.platform,
         "timestamp": curr_time,
         "context": contexts[context_idx],
         "recommendation": suggestions[suggestion_idx],
         "feedback": feedback
      }
      user_activity_entry = {
         "timestamp": curr_time,
         "context": contexts[context_idx],
         "recommendation": suggestions[suggestion_idx],
         "feedback": feedback
      }
      self.general_mab_instance.update_activity(general_activity_entry)
      self.user_mab_instance.update_activity(user_activity_entry)

   # Close db connection:
   def close_db_connection(self):
      self.general_mab_instance.close_db()
      self.user_mab_instance.close_db()