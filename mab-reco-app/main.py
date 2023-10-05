import flet as ft
import datetime
import numpy as np
import hashlib
from MABInstance import MABInstance
from flet.auth.providers import GitHubOAuthProvider
from dotenv import load_dotenv
import os

# Get client ID and client secret:
load_dotenv()
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

# The main function to start the app:
def main(page: ft.Page):
   # page configurations, center content, hide scrollbar, etc.
   page.title = "Stree Relief Recommendation"
   page.vertical_alignment = ft.MainAxisAlignment.CENTER
   page.horizontal_alignment = ft.MainAxisAlignment.CENTER
   page.bgcolor = ft.colors.BROWN_100
   page.scroll = ft.ScrollMode.HIDDEN
   page.padding = 20

   # enable user login:
   provider = GitHubOAuthProvider(
      client_id=GITHUB_CLIENT_ID,
      client_secret=GITHUB_CLIENT_SECRET,
      redirect_url="https://eclipse.usc.edu/api/oauth/redirect",
   )

   # when login button is clicked:
   def login_click(e):
      page.login(provider)

   # when logout in button is clicked:
   def logout_click(e, mab_instance):
      mab_instance.close_db_connection()
      page.logout()

   # upon login:
   def on_login(e):
      # global mab_instance, contexts, suggestions
      if not e.error:
         user_id = page.auth.user.id
         # print("User ID:", page.auth.user.id)
         # Create a hash object (SHA-512)
         hash_object = hashlib.sha256()
         hash_object.update(user_id.encode())
         user_hash = hash_object.hexdigest()
         # Update mab_instance with user hash:
         mab_instance = MABInstance(user_hash, True, 'pwa')
         # remove login button, and add context selection:
         page.controls.pop()
         page.add(get_context_container(mab_instance))
         page.update()
   
   # upon logout:
   def on_logout(e):
      page.controls.pop()
      page.add(login_button_container)
      page.update()

   # login-button:
   login_button_container = ft.Container(
      content=ft.Container(
         content=ft.Text('Login with GitHub', size=20, color=ft.colors.BLACK, font_family='Tahoma', text_align='CENTER'),
         margin=10,
         padding=10,
         bgcolor=ft.colors.WHITE30,
         width=210,
         height=70,
         border_radius=20,
         alignment=ft.alignment.center,
         ink=True,
         on_click=lambda e: login_click(e),
      ),
      alignment=ft.alignment.center,
      margin=30,
      padding=30
   )

   # add login_button:
   page.on_login = on_login
   page.on_logout = on_logout
   page.add(login_button_container)

   # define controls (widgets):
   # --------------------------------------------------------------------------------------------------------------------
   # contexts container:
   def get_context_container(mab_instance):
      contexts = mab_instance.get_contexts()
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
            on_click=lambda e, context=context, mab_instance=mab_instance: select_context(e, context, mab_instance),
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
               ),
               ft.Container(
                  content=ft.Text('Logout', size=17, color=ft.colors.BLACK, font_family='Tahoma', text_align='CENTER'),
                  margin=10,
                  padding=10,
                  bgcolor=ft.colors.BROWN_100,
                  alignment=ft.alignment.bottom_center,
                  ink=True,
                  on_click=lambda e, mab_instance=mab_instance: logout_click(e, mab_instance),
               ),
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
   def get_suggestion_container(context_index, prev_sugg_indices, mab_instance):
      suggestions = mab_instance.get_suggestions()
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
               on_click=lambda e, 
                  suggestion=suggestion, 
                  context_index=context_index, 
                  prev_sugg_indices=prev_sugg_indices,
                  mab_instance=mab_instance: select_suggestion(e, suggestion, context_index, prev_sugg_indices, mab_instance),
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
                     on_click=lambda e, mab_instance=mab_instance: restart_suggestion(e, mab_instance),
                  ),
                  ft.Container(
                     content=ft.Text('Logout', size=17, color=ft.colors.BLACK, font_family='Tahoma', text_align='CENTER'),
                     margin=10,
                     padding=10,
                     bgcolor=ft.colors.BROWN_100,
                     alignment=ft.alignment.bottom_center,
                     ink=True,
                     on_click=lambda e, mab_instance=mab_instance: logout_click(e, mab_instance),
                  ),
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
   def get_feedback_container(context_index, suggestion_index, prev_sugg_indices, mab_instance):
      if suggestion_index == -1:
         feedback = -1
         # update data & history data file:
         mab_instance.update_mab_file(context_index, suggestion_index, feedback, prev_sugg_indices)
         # show a short message and restart button:
         return get_ending_container(feedback, mab_instance)
      else:
         # show suggestion image and description:
         suggestions = mab_instance.get_suggestions()
         suggestion_image_url = f'/assets/images/{suggestions[suggestion_index]}.png'
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
                                 prev_sugg_indices=prev_sugg_indices,
                                 mab_instance=mab_instance: select_feedback(e, context_index, suggestion_index, feedback, prev_sugg_indices, mab_instance),
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
                     on_click=lambda e, mab_instance=mab_instance: restart_suggestion(e, mab_instance),
                  ),
                  ft.Container(
                     content=ft.Text('Logout', size=17, color=ft.colors.BLACK, font_family='Tahoma', text_align='CENTER'),
                     margin=10,
                     padding=10,
                     bgcolor=ft.colors.BROWN_100,
                     alignment=ft.alignment.bottom_center,
                     ink=True,
                     on_click=lambda e, mab_instance=mab_instance: logout_click(e, mab_instance),
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
   def get_ending_container(feedback, mab_instance):
      if feedback == -1:
         ending_message = "Oops... Looks like you didn't like all the activities we just gave you.\n\nWe will add more options, please come back next time!"
      elif feedback == 0:
         ending_message = "Uh-oh... I'm sorry this activity isn't helpful to you. We will add more activities. Thank you for your time and patience."
      elif feedback <= 3:
         ending_message = "That's great! I'm glad you tried our activity. We will make further improvements. Until next time!"
      else:
         ending_message = "Excellent! I'm glad our activity helped. Have a nice day!"    
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
                  on_click=lambda e, mab_instance=mab_instance: restart_suggestion(e, mab_instance),
               ),
               ft.Container(
                  content=ft.Text('Logout', size=18, color=ft.colors.BLACK, font_family='Tahoma', text_align='CENTER'),
                  margin=10,
                  padding=10,
                  bgcolor=ft.colors.WHITE30,
                  width=210,
                  height=70,
                  border_radius=20,
                  alignment=ft.alignment.center,
                  ink=True,
                  on_click=lambda e, mab_instance=mab_instance: logout_click(e, mab_instance),
               ),
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
   def select_context(e, context, mab_instance):
      contexts = mab_instance.get_contexts()
      # get context index:
      context_index = contexts.index(context)
      # removes the entire context widget, update page, then add suggestion control widget:
      page.controls.pop()
      # get first round suggestions:
      prev_sugg_indices = []
      page.add(get_suggestion_container(context_index, prev_sugg_indices, mab_instance))
      page.update()

   # gets the suggestion of which the user clicked:
   def select_suggestion(e, suggestion, context_index, prev_sugg_indices, mab_instance):
      if suggestion == 'Something Else':
         # remove old control:
         page.controls.pop()
         suggestion_container = get_suggestion_container(context_index, prev_sugg_indices, mab_instance)
         if suggestion_container == "Failed to suggest":
            page.add(get_feedback_container(context_index, -1, prev_sugg_indices, mab_instance))
         else:
            page.add(suggestion_container)
      else:
         suggestion_index = mab_instance.get_suggestion_index(suggestion)
         page.controls.pop()
         page.add(get_feedback_container(context_index, suggestion_index, prev_sugg_indices, mab_instance))
      # update page:
      page.update()

   # gets feedback:
   def select_feedback(e, context_index, suggestion_index, feedback, prev_sugg_indices, mab_instance):
      # update activity and mab data files:
      curr_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      mab_instance.update_activity_log(curr_time, context_index, suggestion_index, feedback)
      mab_instance.update_mab_file(context_index, suggestion_index, feedback, prev_sugg_indices)
      # remove feedback container, add ending scene:
      page.controls.pop()
      page.add(get_ending_container(feedback, mab_instance))
      page.update()

   # restart:
   def restart_suggestion(e, mab_instance):
      page.controls.pop()
      page.add(get_context_container(mab_instance))
      page.update()
   # --------------------------------------------------------------------------------------------------------------------

# run the app:
if __name__ == "__main__":
   ft.app(target=main, view=ft.WEB_BROWSER, port=5000)