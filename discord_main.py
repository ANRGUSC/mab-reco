import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv
import datetime
import pytz
import numpy as np
from MABInstance import MABInstance

# Get bot token:
load_dotenv()
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Set thread section and interaction timeout duration:
thread_section_duration = 60 * 24         # (mins & hours) e.g. 24 hours, 1 day

# Enable the message_content intent
intents = discord.Intents.all()

# Set bot command prefix: e.g. /hello
bot = commands.Bot(command_prefix = '/', intents = intents)

# When the bot is online, show a short message:
@bot.event
async def on_ready():
   print("Bot is online!")

# When new member joins the server, send out a greeting message:
@bot.event
async def on_member_join(member):
   # Get the text channels the member is in
   member_text_channels = [channel for channel in member.guild.text_channels if member in channel.members]

   if member_text_channels:
      # Use the first text channel the member is in:
      channel = member_text_channels[0]
   else:
      # Otherwise, uses the main text channel:
      channel = member.guild.system_channel

   # Send message:
   if channel is not None:
      message = f'{member.display_name} has joined the server!\n\nPlease type "/suggest" to start your suggestion section.'  
      await channel.send(message)

# /suggest command:
@bot.command()
async def suggest(ctx):
   command_generator(ctx)

active_tasks = [] # record all started tasks

# creates tasks to allow concurrency:
def command_generator(ctx):
   # start the thread:
   task = tasks.loop(seconds=1)(suggestion_thread_loop)
   active_tasks.append(task)
   task.start(ctx, task)

# suggest thread loop:
async def suggestion_thread_loop(ctx, task):
   # create thread for the user:
   utc_now = datetime.datetime.utcnow()
   pacific = pytz.timezone('US/Pacific')
   pdt_now = pacific.fromutc(utc_now)
   curr_time = pdt_now.strftime("%Y-%m-%d %H:%M")
   thread = await ctx.channel.create_thread(
      name = f"{curr_time}: Recommendation channel for <{ctx.author.display_name}>",
      auto_archive_duration = thread_section_duration
   )
   
   # add user:
   await thread.add_user(ctx.author)
   
   # Tells the user where to start the recommendation process:
   await ctx.send(f"For <{ctx.author.display_name}>: Click here to have your customized recommendation {thread.mention}")

   # check user's response:
   def check(response):
      return response.author == ctx.author and response.channel == thread and not thread.locked and not thread.archived

   # create mab instance:
   mab_instance = MABInstance(ctx.author.id, True, "discord")
   # get contexts:
   contexts = mab_instance.get_contexts()

   # send initial suggestions message:
   message = "Which of the following scenarios are you in right now:\n"
   for i, context in enumerate(contexts, start = 1):
      message += f"\n{i}. {context}\n"
   message += "\nType in the chat with the number of your choice."
   await thread.send(message)
   
   # get context response from user:
   while True:
      context_response = await bot.wait_for('message', check=check) 
      try:
         context_index = int(context_response.content) - 1
         if 0 <= context_index < len(contexts):
            break
         else:
            await thread.send(f"Uh-oh...Please select a context with a number input from 1 to {len(contexts)}.")
      except ValueError:
         if context_response.content == "/suggest":
            await thread.send("Please return to the main chat channel to start a new recommendation session.")
         else:
            await thread.send(f"Sorry we only accept numbers for context selection. Please select a context with a number input from 1 to {len(contexts)}.")

   # send suggestions and wait for user's reaction to suggestion
   first_round = True
   fail_to_suggest = False
   prev_sugg_indices = []  # record all suggestions indices given to the user
   suggestions = mab_instance.get_suggestions()

   while True:
      sugg_list = mab_instance.make_recommendation(context_index, prev_sugg_indices)
      # there are no more suggestions, break the loop:
      if len(sugg_list) == 0:
         fail_to_suggest = True
         break
      
      sugg_indices = np.where(np.isin(suggestions, sugg_list))[0]
      prev_sugg_indices = np.unique(np.concatenate((prev_sugg_indices, sugg_indices)).astype(int))

      if first_round:
         first_round = False
         message = "Please wait a moment while we fetch your suggestions..."
         message += "\n\nYay! Here they are. Choose what you want to do most right now.\n\nIf you don't like any of the recommendations, simply reply 0.\n"
         for i, sugg in enumerate(sugg_list, start = 1):
            message += f"\n{i}. {sugg}\n"
         await thread.send(message)
      else:
         message = "Don't worry! Let's try this again, One moment please..."
         message += "\n\nYay! Here they are. Choose what you want to do most right now.\n\nIf you don't like any of the recommendations, simply reply 0.\n"
         for i, sugg in enumerate(sugg_list, start = 1):
            message += f"\n{i}. {sugg}\n"
         await thread.send(message)

      # get user response for recommendations:
      while True:
         suggestion_response = await bot.wait_for('message', check=check)
         try: 
            sugg_idx = int(suggestion_response.content) - 1
            if -1 <= sugg_idx < len(sugg_list):
               break
            else:
               await thread.send(f"Uh-oh...Please select an activity with a number input from 0 to {len(sugg_list)}.")
         except ValueError:
            if suggestion_response.content == "/suggest":
               await thread.send("Please return to the main chat channel to start a new recommendation session.")
            else:
               await thread.send(f"Sorry we only accept numbers for activity selection. Please select an activity with a number input from 0 to {len(sugg_list)}.")

      if sugg_idx == -1:
         suggestion_index = -1
      else:
         suggestion_index = mab_instance.get_suggestion_index(sugg_list[sugg_idx])
         break

   # based on whether made a successful suggestion, behave properly:
   if fail_to_suggest:
      feedback_rating = -1
      await thread.send("Oops...Looks like you didn't like all the activities we just gave you.\n\nWe will add more options, please come back next time!")
   else:
      # send instruction & image for activity and get user feedback:
      with open(mab_instance.get_suggestion_Image(suggestion_index), 'rb') as image_file:
         sugg_image = discord.File(image_file)
         await thread.send(file=sugg_image)
         await thread.send("\n\u200b")
      message = f"Great! {mab_instance.get_suggestion_description(suggestion_index)}"
      message += "\n\nTake your time! Once you are done, please provide a feedback from 0 (unhelpful) to 5 (out of this world) so we can better help you next time!"
      await thread.send(message)
   
      while True:
         feedback_response = await bot.wait_for('message', check=check)
         try:
            feedback_rating = int(feedback_response.content)
            if 0 <= feedback_rating <= 5:
               break
            else:
               await thread.send("Uh-oh...Please give us a feedback from 0 to 5.")
         except ValueError:
            if feedback_response.content == "/suggest":
               await thread.send("Please return to the main chat channel to start a new recommendation session.")
            else:
               await thread.send("Sorry we only accept numbers for feedback. Please give us a feedback from 0 to 5.")
      
      # Last bot message for this thread:
      if feedback_rating == 0:
         await thread.send("Uh-oh... I'm sorry this activity isn't helpful to you. We will add more activities. Thank you for your time and patience.")
      elif feedback_rating <= 3:
         await thread.send("That's great! I'm glad you tried our activity. We will make further improvements. Until next time!")
      else:
         await thread.send("Excellent! I'm glad our activity helped. Have a nice day!")

      # update activity in both user's own activity history, and the total activity history
      utc_now = datetime.datetime.utcnow()
      pacific = pytz.timezone('US/Pacific')
      pdt_now = pacific.fromutc(utc_now)
      curr_time = pdt_now.strftime("%Y-%m-%d %H:%M:%S")
      mab_instance.update_activity_log(curr_time, context_index, suggestion_index, feedback_rating)

   # cancel task:
   task.cancel()

   # update data & history data file:
   mab_instance.update_mab_file(context_index, suggestion_index, feedback_rating, prev_sugg_indices)

   # close database connection:
   mab_instance.close_db_connection()

# Run the bot:
bot.run(BOT_TOKEN)