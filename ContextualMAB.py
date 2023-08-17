# This is the MAB class object implemented with the Upper Confidence Bound Algorithm.

import numpy as np

class ContextualMAB:
   def __init__(self, num_suggestions, num_contexts, exploration_param, history_data_file=None):
      self.num_suggestions = num_suggestions
      self.num_contexts = num_contexts
      self.exploration_param = exploration_param

      # rewards is a num_arms (rows) x num_contexts (columns) matrix:
      self.rewards = np.zeros((num_suggestions, num_contexts))
      # records how many combination is picked:
      self.selections = np.zeros((num_suggestions, num_contexts))
      # record mab_scores:
      self.mab_scores = np.full((num_suggestions, num_contexts), float('inf'))
      # records total number of selections so far
      self.total_selections = 0

      # if a history data file is given, update parameters from it:
      if history_data_file is not None:
         self.read_hist_file(history_data_file)

   # Recommend the top rec_size suggestions based on given context:
   def recommend(self, rec_size, context_index, first_time):
      # records all mab scores for the given context for different suggestions
      context_mab_scores = self.mab_scores[:, context_index]
      # rec_size <= self.num_suggestions (gives an array of indices of size rec_size with largest ucb_score):
      if first_time:
         return np.random.choice(len(context_mab_scores), size=rec_size, replace=False)
      else:
         return np.argsort(context_mab_scores)[-rec_size:][::-1]

   # This is called when the user has made a choice for one of the suggestions:
   def update(self, feedback_score, suggestion_index, context_index):
      # Suppose the feedback_score is in the range from 0 - 5: 0 implies no selection/unhelpful, where as 5 implies extremely helpful
      self.rewards[suggestion_index][context_index] = self.rewards[suggestion_index][context_index] + feedback_score
      self.total_selections += 1
      self.selections[suggestion_index][context_index] += 1
      # update mab score:
      self.update_mab_score(suggestion_index, context_index)

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
   
   # # update the exploration parameter based on performance:
   # def update_exploration_param(self):
   #    return

   # read parameter data from a data file:
   def read_hist_file(self, history_data_file):
      matrices = {"Rewards": None, "Selections": None, "MAB Scores": None}
      current_matrix = None
      try:
         with open(history_data_file, "r") as file:
            # first line, disregard:
            first_line = file.readline()  
            self.total_selections = int(file.readline().strip())

            for line in file:
               line = line.strip()
               if line in ["Rewards", "Selections", "MAB Scores"]:
                  current_matrix = line
                  matrices[current_matrix] = []
               elif line:
                  matrix_row = [float(num) for num in line.strip().split()]
                  matrices[current_matrix].append(matrix_row)

         # Convert lists of lists to NumPy arrays
         rewards = np.array(matrices["Rewards"])
         selections = np.array(matrices["Selections"])
         mab_scores = np.array(matrices["MAB Scores"])
         self.rewards[:, :] = rewards
         self.selections[:, :] = selections
         self.mab_scores[:, :] = mab_scores
      except FileNotFoundError:
         print("This history data file does not exist.")
         exit(1)

   # write current data into a data file:
   def write_hist_file(self, output_file):
      matrices = {"Rewards": self.rewards, "Selections": self.selections, "MAB Scores": self.mab_scores}
      
      with open(output_file, "w") as file:
         # Write total selections first:
         file.write("Total Selections:\n")
         file.write(f"{self.total_selections}\n\n")

         for matrix_name, matrix_data in matrices.items():
            # write matrix header:
            file.write(f"{matrix_name}\n")
            # write matrix data:
            for row in matrix_data:
               file.write(" ".join(str(num) for num in row) + "\n")
            # leave a line between matrices
            file.write("\n")

   # update user log history:
   def update_activity_log(self, activity_file, activity_entry):
      with open(activity_file, "a") as file:
         file.write(activity_entry)