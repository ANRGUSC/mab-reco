import discord
from discord.ext import commands, tasks
import asyncio
import os
from dotenv import load_dotenv
import datetime
import numpy as np
from MABInstance import MABInstance

# Get bot token:
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

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
   channel = member.guild.system_channel
   if channel is not None:
      message = f'{member.name} has joined the server! Welcome!'
      await channel.send(message)

# /suggest command:
@bot.command()
async def suggest(ctx):
   # create mab instance:
   mab_instance = MABInstance(ctx.author.id, True)

   # get contexts:
   contexts = mab_instance.get_contexts()

   # create thread for the user:
   curr_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
   thread = await ctx.channel.create_thread(
      name = f"{curr_time}: Recommendation channel for <{ctx.author.display_name}>",
      auto_archive_duration = 60 * 24 * 3
   )

   # add user:
   await thread.add_user(ctx.author)

   # Tells the user where to start the recommendation process:
   await ctx.send(f"For <{ctx.author.display_name}>: Click here to have your customized recommendation {thread.mention}")

   # send initial suggestions message:
   message = "Which of the following scenarios are you in right now:\n"
   for i, context in enumerate(contexts, start = 1):
      message += f"\n{i}. {context}\n"
   message += "\nType in the chat with the number of your choice."
   await thread.send(message)

   # start the thread:
   suggestion_thread_loop.start(ctx.author, thread, mab_instance)

# suggest thread loop:
@tasks.loop(seconds=1)
async def suggestion_thread_loop(user, thread, mab_instance):
   # check user's response:
   def check(response):
      return response.author == user and response.channel == thread and not thread.locked and not thread.archived

   # context list:
   contexts = mab_instance.get_contexts()

   # get context response from user:
   try:
      while True:
         context_response = await bot.wait_for('message', check=check, timeout=900) 
         try:
            context_index = int(context_response.content) - 1
            if 0 <= context_index < len(contexts):
               break
            else:
               await thread.send("Invalid context selection. Please enter a valid number.")
         except ValueError:
            await thread.send("Invalid input. Please enter numbers only.")
   except asyncio.TimeoutError:
      await thread.send("uh-oh! Activity was cancelled due to long time no response. See you next time!")
      suggestion_thread_loop.cancel()
      return

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
      try:
         while True:
            suggestion_response = await bot.wait_for('message', check=check, timeout=900)
            try: 
               sugg_idx = int(suggestion_response.content) - 1
               if -1 <= sugg_idx < len(sugg_list):
                  break
               else:
                  await thread.send("Invalid activity selection. Please enter a valid number.")
            except ValueError:
               await thread.send("Invalid input. Please enter numbers only.")
      except asyncio.TimeoutError:
         await thread.send("uh-oh! Activity was cancelled due to long time no response. See you next time!")
         suggestion_thread_loop.cancel() 
         return

      if sugg_idx == -1:
         suggestion_index = -1
      else:
         suggestion_index = mab_instance.get_suggestion_index(sugg_list[sugg_idx])
         break

   # based on whether made a successful suggestion, behave properly:
   if fail_to_suggest:
      feedback_rating = -1
      await thread.send("Oops... Looks like you didn't like all the activities we just gave you.\n\nWe will add more options, please come back next time!")
   else:
      # send instruction & image for activity and get user feedback:
      with open(mab_instance.get_suggestion_Image(suggestion_index), 'rb') as image_file:
         sugg_image = discord.File(image_file)
         await thread.send(file=sugg_image)
         await thread.send("\n\u200b")
      message = f"Great! {mab_instance.get_suggestion_description(suggestion_index)}"
      message += "\n\nTake your time! Once you are done, please provide a feedback from 0 (unhelpful) to 5 (out of this world) so we can better help you next time!"
      await thread.send(message)
   
      try:
         while True:
            feedback_response = await bot.wait_for('message', check=check, timeout=3600)
            try:
               feedback_rating = int(feedback_response.content)
               if 0 <= feedback_rating <= 5:
                  break
               else:
                  await thread.send("Invalid feedback. Please enter a feedback from 0 ~ 5.")
            except ValueError:
               await thread.send("Invalid input. Please enter numbers only.")
      except asyncio.TimeoutError:
         await thread.send("uh-oh! Activity was cancelled due to long time no response. See you next time!")
         suggestion_thread_loop.cancel()
         return

      # Last bot message for this thread:
      await thread.send("Excellent! Hope you feel better after this activity! See you next time!")

      # update activity in both user's own activity history, and the total activity history
      curr_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
      mab_instance.update_activity_log(curr_time, context_index, suggestion_index, feedback_rating)

   # stop looping:
   suggestion_thread_loop.cancel()

   # update data & history data file:
   mab_instance.update_mab_file(context_index, suggestion_index, feedback_rating, prev_sugg_indices)

# Run the bot:
bot.run(BOT_TOKEN)