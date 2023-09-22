import flet as ft
import datetime
import time
import numpy as np
import os
import hashlib
from MABInstance import MABInstance

# Context Control (widget) class object:
# -----------------------------------------------------------------------------------------------------------------------------
class ContextControl(ft.UserControl):
   def __init__(self, mab_instance, page):
      super().__init__()
      self.mab_instance = mab_instance
      self.contexts = self.mab_instance.get_contexts()
      self.page = page
      # a list of clickable options to show contexts:
      self.context_options = [
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
            on_click=lambda e, context=context: self.select_context(context),
         ) for context in self.contexts
      ]
      # the contexts selection container:
      self.context_container = ft.Container(
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
                     self.context_options
                  ),
               )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
         ),
         alignment=ft.alignment.center,
         margin=20,
         padding=30
      )

   # gets the context of which the user clicked, then remove the context selection widget:
   def select_context(self, context):
      # get context index:
      context_index = self.contexts.index(context)
      # removes the entire context widget, update page, then add suggestion control widget:
      self.page.controls.pop()
      self.page.add(SuggestControl(self.mab_instance, self.page, context_index))
      self.page.update()
   
   # return the control:
   def build(self):
      return self.context_container
# -----------------------------------------------------------------------------------------------------------------------------

# Suggest Control (widget) class object:
# -----------------------------------------------------------------------------------------------------------------------------
class SuggestControl(ft.UserControl):
   def __init__(self, mab_instance, page, context_index):
      super().__init__()
      self.mab_instance = mab_instance
      self.contexts = self.mab_instance.get_contexts()
      self.page = page
      self.context_index = context_index
      self.suggestions = self.mab_instance.get_suggestions()
      # get first round suggestions:
      self.prev_sugg_indices = []
      self.sugg_list = self.mab_instance.make_recommendation(self.context_index, self.prev_sugg_indices)
      # get container:
      self.suggestion_container = self.get_container()

   def get_container(self):
      # append "Maybe something else" in sugg_list first:
      self.sugg_list.append('Maybe something else')
      # a list of clickable options to show contexts:
      suggestion_options = [
         ft.Container(
            content=ft.Text(f'{suggestion}', size=20, color=ft.colors.BLACK, font_family='Tahoma', text_align='JUSTIFY'),
            margin=10,
            padding=10,
            bgcolor=ft.colors.WHITE30,
            width=210,
            height=70,
            border_radius=20,
            alignment=ft.alignment.center,
            ink=True,
            on_click=lambda e, suggestion=suggestion: self.select_suggestion(suggestion),
         ) for suggestion in self.sugg_list
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
               )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
         ),
         alignment=ft.alignment.center,
         margin=20,
         padding=30
      )
      # remove "Maybe something else" from sugg_list:
      self.sugg_list.pop()
      return suggestion_container
   
   # gets the suggestion of which the user clicked:
   def select_suggestion(self, suggestion):
      if suggestion == 'Maybe something else':
         # append the suggestion indices to prev_sugg_indices first:
         sugg_indices = np.where(np.isin(self.suggestions, self.sugg_list))[0]
         self.prev_sugg_indices = np.unique(np.concatenate((self.prev_sugg_indices, sugg_indices)).astype(int))
         # get new sugg_list:
         self.sugg_list = self.mab_instance.make_recommendation(self.context_index, self.prev_sugg_indices)
         # remove old control:
         self.page.controls.pop()
         # if sugg_list is empty:
         if len(self.sugg_list) == 0:
            print("Failed to suggest!")
         else:
            # get new suggestion_container:
            self.suggestion_container = self.get_container()
            self.page.add(self.suggestion_container)
            self.page.update()
      else:
         suggestion_index = self.mab_instance.get_suggestion_index(suggestion)
         self.page.controls.pop()
         print("Jump to next step!")
         # self.page.add(SuggestControl(self.mab_instance, self.page, context_index))
         self.page.update()
 
   # return the control:
   def build(self):
      return self.suggestion_container
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

   # page configurations, center content, hide scrollbar, etc.
   page.title = "Stree Relief Recommendation"
   page.vertical_alignment = ft.MainAxisAlignment.CENTER
   page.horizontal_alignment = ft.MainAxisAlignment.CENTER
   page.bgcolor = ft.colors.BROWN_100
   page.scroll = ft.ScrollMode.HIDDEN
   
   # add page containers:
   context_control = ContextControl(mab_instance, page)
   page.add(context_control)

# run the app:
ft.app(target=main)