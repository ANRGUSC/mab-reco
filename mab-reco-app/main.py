import flet as ft
import datetime
import time
import numpy as np
import os
import hashlib
from MABInstance import MABInstance

# Context Control (widget) class object:
# -----------------------------------------------------------------------------------------------------------------------------
# class ContextControl(ft.UserControl):
#    def __init__(self, mab_instance, page):
#       super().__init__()
#       self.mab_instance = mab_instance
#       self.contexts = self.mab_instance.get_contexts()
#       self.page = page
#       # a list of clickable options to show contexts:
#       self.context_options = [
#          ft.Container(
#             content=ft.Text(f'{context}', size=20, color=ft.colors.BLACK, font_family='Tahoma', text_align='JUSTIFY'),
#             margin=10,
#             padding=10,
#             bgcolor=ft.colors.WHITE30,
#             width=210,
#             height=70,
#             border_radius=20,
#             alignment=ft.alignment.center,
#             ink=True,
#             on_click=lambda e, context=context: self.select_context(context),
#          ) for context in self.contexts
#       ]
#       # the contexts selection container:
#       self.context_container = ft.Container(
#          content=ft.Column(
#             [  
#                ft.Container(
#                   content=ft.Text('Greetings! Which of the following scenario are you in right now:', size=20, color=ft.colors.BROWN_900, font_family='Tahoma', text_align='CENTER'),
#                   bgcolor=ft.colors.BLACK12,
#                   border_radius=20,
#                   margin=10,
#                   padding=10,
#                ),
#                ft.Container(
#                   content= ft.Column(
#                      self.context_options
#                   ),
#                )
#             ],
#             alignment=ft.MainAxisAlignment.CENTER,
#             horizontal_alignment=ft.CrossAxisAlignment.CENTER,
#          ),
#          alignment=ft.alignment.center,
#          margin=20,
#          padding=30
#       )

#    # gets the context of which the user clicked, then remove the context selection widget:
#    def select_context(self, context):
#       # get context index:
#       context_index = self.contexts.index(context)
#       # removes the entire context widget, update page, then add suggestion control widget:
#       self.page.controls.pop()
#       self.page.add(SuggestControl(self.mab_instance, self.page, context_index))
#       self.page.update()
   
#    # return the control:
#    def build(self):
#       return self.context_container
# -----------------------------------------------------------------------------------------------------------------------------

# Suggest Control (widget) class object:
# -----------------------------------------------------------------------------------------------------------------------------
# class SuggestControl(ft.UserControl):
#    def __init__(self, mab_instance, page, context_index):
#       super().__init__()
#       self.mab_instance = mab_instance
#       self.contexts = self.mab_instance.get_contexts()
#       self.page = page
#       self.context_index = context_index
#       self.suggestions = self.mab_instance.get_suggestions()
#       # get first round suggestions:
#       self.prev_sugg_indices = []
#       self.sugg_list = self.mab_instance.make_recommendation(self.context_index, self.prev_sugg_indices)
#       # get container:
#       self.suggestion_container = self.get_container()

#    def get_container(self):
#       # append "Maybe something else" in sugg_list first:
#       self.sugg_list.append('Maybe something else')
#       # a list of clickable options to show contexts:
#       suggestion_options = [
#          ft.Container(
#             content=ft.Text(f'{suggestion}', size=20, color=ft.colors.BLACK, font_family='Tahoma', text_align='JUSTIFY'),
#             margin=10,
#             padding=10,
#             bgcolor=ft.colors.WHITE30,
#             width=210,
#             height=70,
#             border_radius=20,
#             alignment=ft.alignment.center,
#             ink=True,
#             on_click=lambda e, suggestion=suggestion: self.select_suggestion(suggestion),
#          ) for suggestion in self.sugg_list
#       ]
#       # the contexts selection container:
#       suggestion_container = ft.Container(
#          content=ft.Column(
#             [  
#                ft.Container(
#                   content=ft.Text('What do you like to do now?', size=20, color=ft.colors.BROWN_900, font_family='Tahoma', text_align='CENTER'),
#                   bgcolor=ft.colors.BLACK12,
#                   border_radius=20,
#                   margin=10,
#                   padding=10,
#                ),
#                ft.Container(
#                   content= ft.Column(
#                      suggestion_options
#                   ),
#                )
#             ],
#             alignment=ft.MainAxisAlignment.CENTER,
#             horizontal_alignment=ft.CrossAxisAlignment.CENTER,
#          ),
#          alignment=ft.alignment.center,
#          margin=20,
#          padding=30
#       )
#       # remove "Maybe something else" from sugg_list:
#       self.sugg_list.pop()
#       return suggestion_container
   
#    # gets the suggestion of which the user clicked:
#    def select_suggestion(self, suggestion):
#       if suggestion == 'Maybe something else':
#          # append the suggestion indices to prev_sugg_indices first:
#          sugg_indices = np.where(np.isin(self.suggestions, self.sugg_list))[0]
#          self.prev_sugg_indices = np.unique(np.concatenate((self.prev_sugg_indices, sugg_indices)).astype(int))
#          # get new sugg_list:
#          self.sugg_list = self.mab_instance.make_recommendation(self.context_index, self.prev_sugg_indices)
#          # remove old control:
#          self.page.controls.pop()
#          # if sugg_list is empty:
#          if len(self.sugg_list) == 0:
#             print("Failed to suggest!")
#          else:
#             # get new suggestion_container:
#             self.suggestion_container = self.get_container()
#             self.page.add(self.suggestion_container)
#             self.page.update()
#       else:
#          suggestion_index = self.mab_instance.get_suggestion_index(suggestion)
#          self.page.controls.pop()
#          print("Jump to next step!")
#          # self.page.add(SuggestControl(self.mab_instance, self.page, context_index))
#          self.page.update()
 
#    # return the control:
#    def build(self):
#       return self.suggestion_container
# -----------------------------------------------------------------------------------------------------------------------------

# The main function to start the app:
def main(page: ft.Page):
   # add oauth for user login and design user hash code in here:
   user_id = "2190310"

   # Create a hash object (SHA-512)
   hash_object = hashlib.sha256()
   hash_object.update(user_id.encode())
   user_hash = hash_object.hexdigest()

   # print(user_hash)

   # declear mab instance:
   mab_instance = MABInstance(user_hash, True, 'pwa')
   contexts = mab_instance.get_contexts()
   suggestions = mab_instance.get_suggestions()

   # define controls (widgets):
   # --------------------------------------------------------------------------------------------------------------------
   # contexts container:
   def get_context_container():
      context_options = [
         ft.Container(
            content=ft.Text(f'{context}', size=20, color=ft.colors.BLACK, font_family='Tahoma', text_align='JUSTIFY'),
            margin=10,
            padding=10,
            bgcolor=ft.colors.WHITE30,
            width=210,
            height=70,
            border_radius=20,
            alignment=ft.alignment.center,
            ink=True,
            on_click=lambda e, context=context: select_context(e, context),
         ) for context in contexts
      ]
      # the contexts selection container:
      context_container = ft.Container(
         content=ft.Column(
            [  
               ft.Container(
                  content=ft.Text('Greetings! Which of the following scenario are you in right now:', size=20, color=ft.colors.BROWN_900, font_family='Tahoma', text_align='CENTER'),
                  bgcolor=ft.colors.BLACK12,
                  border_radius=20,
                  margin=10,
                  padding=10,
               ),
               ft.Container(
                  content= ft.Column(
                     context_options
                  ),
               )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
         ),
         alignment=ft.alignment.center,
         margin=30,
         padding=30
      )
      return context_container

   # updates and get suggestion_container:
   def get_suggestion_container(context_index, prev_sugg_indices):
      # get suggestion list:
      sugg_list = mab_instance.make_recommendation(context_index, prev_sugg_indices)
      # if sugg_list is empty:
      if len(sugg_list) == 0:
         return "Failed to suggest"
      else:
         # append new indices to prev_sugg_indices:
         sugg_indices = np.where(np.isin(suggestions, sugg_list))[0]
         prev_sugg_indices = np.unique(np.concatenate((prev_sugg_indices, sugg_indices)).astype(int))
         # append "Something Else" in sugg_list first:
         sugg_list.append('Something Else')
         # a list of clickable options to show contexts:
         suggestion_options = [
            ft.Container(
               content=ft.Text(f'{suggestion}', size=18, color=ft.colors.BLACK, font_family='Tahoma', text_align='CENTER'),
               margin=10,
               padding=10,
               bgcolor=ft.colors.WHITE30,
               width=210,
               height=70,
               border_radius=20,
               alignment=ft.alignment.center,
               ink=True,
               on_click=lambda e, suggestion=suggestion, context_index=context_index, prev_sugg_indices=prev_sugg_indices: select_suggestion(e, suggestion, context_index, prev_sugg_indices),
            ) for suggestion in sugg_list
         ]
         # the contexts selection container:
         suggestion_container = ft.Container(
            content=ft.Column(
               [  
                  ft.Container(
                     content=ft.Text('What do you like to do now?', size=20, color=ft.colors.BROWN_900, font_family='Tahoma', text_align='CENTER'),
                     bgcolor=ft.colors.BLACK12,
                     border_radius=20,
                     margin=10,
                     padding=10,
                  ),
                  ft.Container(
                     content= ft.Column(
                        suggestion_options
                     ),
                  ),
                  ft.Container(
                     content=ft.Text('Restart', size=17, color=ft.colors.BLACK, font_family='Tahoma', text_align='CENTER'),
                     margin=10,
                     padding=10,
                     bgcolor=ft.colors.BROWN_100,
                     alignment=ft.alignment.bottom_center,
                     ink=True,
                     on_click=lambda e: restart_suggestion(e),
                  )
               ],
               alignment=ft.MainAxisAlignment.CENTER,
               horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            alignment=ft.alignment.center,
            margin=30,
            padding=30
         )
         # remove "Something Else" from sugg_list:
         sugg_list.pop()
         return suggestion_container
   
   # get feedback container:
   def get_feedback_container(context_index, suggestion_index, prev_sugg_indices):
      if suggestion_index == -1:
         feedback = -1
         # update data & history data file:
         mab_instance.update_mab_file(context_index, suggestion_index, feedback, prev_sugg_indices)
         # show a short message and restart button:
         return get_ending_container(feedback)
      else:
         # show suggestion image and description:
         suggestion_image_url = mab_instance.get_suggestion_Image(suggestion_index)
         suggestion_description = mab_instance.get_suggestion_description(suggestion_index)
         feedback_container = ft.Container(
            content=ft.Column(
               [
                  ft.Image(
                     src=suggestion_image_url,
                     fit=ft.ImageFit.CONTAIN,
                     width=300,
                     height=300,
                     border_radius=20
                  ),
                  ft.Container(
                     content=ft.Text(
                        f'Great! {suggestion_description}\n\n Please give us your feedback based on how you feel after this activity.', 
                        size=17, color=ft.colors.BROWN_900, font_family='Tahoma', text_align='CENTER'),
                     bgcolor=ft.colors.BLACK12,
                     border_radius=20,
                     margin=10,
                     padding=10,
                  ),
                  ft.Container(
                     content= ft.Row(
                        [
                           ft.Container(
                              content=ft.Text(f'{feedback}', size=15, color=ft.colors.BLACK, font_family='Tahoma', text_align='CENTER'),
                              bgcolor=ft.colors.WHITE30,
                              width=40,
                              height=40,
                              border_radius=5,
                              alignment=ft.alignment.center,
                              ink=True,
                              on_click=lambda e, 
                                 context_index=context_index, 
                                 suggestion_index=suggestion_index, 
                                 feedback=feedback, 
                                 prev_sugg_indices=prev_sugg_indices: select_feedback(e, context_index, suggestion_index, feedback, prev_sugg_indices),
                           ) for feedback in range(6)
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                     ),
                  ),
                  ft.Container(
                     content=ft.Text('Restart', size=17, color=ft.colors.BLACK, font_family='Tahoma', text_align='CENTER'),
                     margin=10,
                     padding=10,
                     bgcolor=ft.colors.BROWN_100,
                     alignment=ft.alignment.bottom_center,
                     ink=True,
                     on_click=lambda e: restart_suggestion(e),
                  ),
               ],
               alignment=ft.MainAxisAlignment.CENTER,
               horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            alignment=ft.alignment.center,
            margin=30,
            padding=30,
         )
         return feedback_container
      
   # get end suggestion container (last scene):
   def get_ending_container(feedback):
      if feedback == -1:
         ending_message = "Oops... Looks like you didn't like all the activities we just gave you.\n\nWe will add more options, please come back next time!"
      elif feedback <= 3:
         ending_message = "Thanks for your feedback! We will offer you something better next time!"
      else:
         ending_message = "Excellent! Hope you feel better after this activity! See you next time!"    
      # Get ending container:
      ending_container = ft.Container(
         content=ft.Column(
            [
               ft.Container(
                  content=ft.Text(f'{ending_message}', size=20, color=ft.colors.BROWN_900, font_family='Tahoma', text_align='CENTER'),
                  bgcolor=ft.colors.BLACK12,
                  border_radius=20,
                  margin=10,
                  padding=10,
               ),
               ft.Container(
                  content=ft.Text('Restart', size=18, color=ft.colors.BLACK, font_family='Tahoma', text_align='CENTER'),
                  margin=10,
                  padding=10,
                  bgcolor=ft.colors.WHITE30,
                  width=210,
                  height=70,
                  border_radius=20,
                  alignment=ft.alignment.center,
                  ink=True,
                  on_click=lambda e: restart_suggestion(e),
               )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
         ),
         alignment=ft.alignment.center,
         margin=30,
         padding=30,
      )
      return ending_container
   # --------------------------------------------------------------------------------------------------------------------
   
   # on-click functions:
   # --------------------------------------------------------------------------------------------------------------------
   # gets the context of which the user clicked, then remove the context selection widget, add first round suggestions:
   def select_context(e, context):
      # get context index:
      context_index = contexts.index(context)
      # removes the entire context widget, update page, then add suggestion control widget:
      page.controls.pop()
      # get first round suggestions:
      prev_sugg_indices = []
      page.add(get_suggestion_container(context_index, prev_sugg_indices))
      page.update()

   # gets the suggestion of which the user clicked:
   def select_suggestion(e, suggestion, context_index, prev_sugg_indices):
      if suggestion == 'Something Else':
         # remove old control:
         page.controls.pop()
         suggestion_container = get_suggestion_container(context_index, prev_sugg_indices)
         if suggestion_container == "Failed to suggest":
            page.add(get_feedback_container(context_index, -1, prev_sugg_indices))
         else:
            page.add(suggestion_container)
      else:
         suggestion_index = mab_instance.get_suggestion_index(suggestion)
         page.controls.pop()
         page.add(get_feedback_container(context_index, suggestion_index, prev_sugg_indices))
      # update page:
      page.update()

   # gets feedback:
   def select_feedback(e, context_index, suggestion_index, feedback, prev_sugg_indices):
      # update activity and mab data files:
      curr_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      mab_instance.update_activity_log(curr_time, context_index, suggestion_index, feedback)
      mab_instance.update_mab_file(context_index, suggestion_index, feedback, prev_sugg_indices)
      # remove feedback container, add ending scene:
      page.controls.pop()
      page.add(get_ending_container(feedback))
      page.update()

   # restart:
   def restart_suggestion(e):
      page.controls.pop()
      page.add(get_context_container())
      page.update()

   # go back to previous scene:
   def go_back(e, pre_scene_container):
      page.controls.pop()
      page.add(pre_scene_container())
      page.update()
   # --------------------------------------------------------------------------------------------------------------------
      
   # page configurations, center content, hide scrollbar, etc.
   page.title = "Stree Relief Recommendation"
   page.vertical_alignment = ft.MainAxisAlignment.CENTER
   page.horizontal_alignment = ft.MainAxisAlignment.CENTER
   page.bgcolor = ft.colors.BROWN_100
   page.scroll = ft.ScrollMode.HIDDEN
   page.padding = 20
   
   # add page containers:
   page.add(get_context_container())
   page.update()

# run the app:
ft.app(target=main)