# This is the MAB class object implemented with the Upper Confidence Bound Algorithm.
import os
import yaml
from ContextualMAB import ContextualMAB

# Read from yaml file, get data:
with open("configuration.yaml", "r") as yaml_file:
   data = yaml.safe_load(yaml_file)

reco_size = data["recommendation_size"]
contexts = data["contexts"]
suggestions = data["suggestions"]
sugg_dict = data["sugg_dict"]
avoid_indices = data["avoid_indices"]

# Name file paths:
user_activity_folder_path = os.path.join(os.getcwd(), data["user_activity_folder_name"])
mab_data_folder_path = os.path.join(os.getcwd(), data["mab_data_folder_name"])
image_folder_path = os.path.join(os.getcwd(), data["image_folder_name"])

history_data_file_name = data["history_mab_data_file_name"]
history_activity_file_name = data["history_activity_file_name"]

# If folder not there, create it:
if not os.path.exists(user_activity_folder_path):
   os.mkdir(user_activity_folder_path)
if not os.path.exists(mab_data_folder_path):
   os.mkdir(mab_data_folder_path)
if not os.path.exists(image_folder_path):
   os.mkdir(image_folder_path)

# print(f"{user_activity_folder_path}\n\n{mab_data_folder_path}\n\n{image_folder_path}")

class MABInstance:
   def __init__(self, user_hash, personalization):
      self.user_hash = user_hash
      self.personalization = personalization
      
      # mab data files:
      self.history_data_file = os.path.join(mab_data_folder_path, history_data_file_name)
      self.user_data_file = os.path.join(mab_data_folder_path, f"discord_{user_hash}_mab.txt")
      
      # activity log files:
      self.history_activity_file = os.path.join(user_activity_folder_path, history_activity_file_name)
      self.user_activity_file = os.path.join(user_activity_folder_path, f"discord_{user_hash}_activity.txt")

      self.image_folder_path = image_folder_path
      
      if os.path.exists(self.history_data_file):
         self.general_mab_instance = ContextualMAB(len(suggestions), len(contexts), 2, self.history_data_file)
      else:
         self.general_mab_instance = ContextualMAB(len(suggestions), len(contexts), 2)
      if os.path.exists(self.user_data_file):
         self.user_mab_instance = ContextualMAB(len(suggestions), len(contexts), 2, self.user_data_file)
      else:
         self.user_mab_instance = ContextualMAB(len(suggestions), len(contexts), 2)

   # Returns the contexts:
   def get_contexts(self):
      return contexts

   # Returns the suggestions:
   def get_suggestions(self):
      return suggestions

   # Returns suggestion based on given context:
   def make_recommendation(self, context_idx):
      ctx_avoid_indices = avoid_indices[context_idx]
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
   def update_mab_file(self, context_idx, suggestion_idx, feedback):
      self.general_mab_instance.update(feedback, suggestion_idx, context_idx, self.history_data_file)
      self.user_mab_instance.update(feedback, suggestion_idx, context_idx, self.user_data_file)

   # Update activity log:
   def update_activity_log(self, curr_time, context_idx, suggestion_idx, feedback):
      activity_entry = f"[{curr_time}]\t<{self.user_hash}>---<{contexts[context_idx]}>---<{suggestions[suggestion_idx]}>---<{feedback}>\n"
      self.general_mab_instance.update_activity_log(self.history_activity_file, activity_entry)
      self.user_mab_instance.update_activity_log(self.user_activity_file, activity_entry)   