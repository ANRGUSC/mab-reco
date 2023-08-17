import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv
import datetime
from ContextualMAB import ContextualMAB

# Define suggestions and contexts:
SUGGESTIONS = [
   "Deep Breathing",
   "Quick Walk",
   "Listen to Music",
   "Stretching",
   "Mini Meditation",
   "Hug a Pillow",
   "Count Your Blessings",
   "Savor a Snack",
   "Memory Lane",
   "Drink something"
]
SUGG_INSTRUCT_DICT = {
   "Deep Breathing": "Take slow, deep breaths. Inhale for a count of 4, hold for 4, exhale for 4. Repeat a few times.",
   "Quick Walk": "Step outside for a short walk around your surroundings. Breathe in fresh air and observe your surroundings.",
   "Listen to Music": "Put on a favorite calming song or instrumental music and immerse yourself in the sound.",
   "Stretching": "Do a few simple stretches to loosen tense muscles, like touching your toes or rolling your shoulders.",
   "Mini Meditation": "Find a quiet spot, close your eyes, and concentrate on your breath or a peaceful image for a few minutes.",
   "Hug a Pillow": "Hug a pillow tightly for a comforting sensation and to release tension.",
   "Count Your Blessings": "List three things that went well today and why.",
   "Savor a Snack": "Grab a small, delicious snack, you deserve it.",
   "Memory Lane": "Reminisce about positive memories to evoke happy feelings.",
   "Drink something": "Drink some water or whatever you like."
}
CONTEXTS = [
   "At Work",
   "During Commute",
   "Study Sessions",
   "During Breaks",
   "Before Bed",
   "During Travel"
]
RECO_SIZE = 5

# Get bot token:
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
SERVER_ID = os.getenv("SERVER_ID")
HISTORY_DATA_FILE = os.getenv("HISTORY_DATA_FILE")

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
   # check if this the first time:
   if os.path.exists(HISTORY_DATA_FILE):
      mab_instance = ContextualMAB(len(SUGGESTIONS), len(CONTEXTS), 2, HISTORY_DATA_FILE)
   else:
      mab_instance = ContextualMAB(len(SUGGESTIONS), len(CONTEXTS), 2)

   # check user's response:
   def check(response):
      return response.author == ctx.author and response.channel == ctx.channel

   # send context message first:
   message = f"For <{ctx.author.name}>:\n\nWhich of the following scenarios are you in right now: "
   for i, context in enumerate(CONTEXTS, start = 1):
      message += f"\n{i}. {context}"
   message += "\nType in the chat with the number of your choice."
   await ctx.send(message)
   
   try:
      while True:
         context_response = await bot.wait_for('message', check=check, timeout=300) 
         try:
            context_index = int(context_response.content) - 1
            if 0 <= context_index < len(CONTEXTS):
               break
            else:
               await ctx.send(f"For <{ctx.author.name}>:\n\nInvalid context selection. Please enter a valid number.")
         except ValueError:
            await ctx.send(f"For <{ctx.author.name}>:\n\nInvalid input. Please enter numbers only.")
   except asyncio.TimeoutError:
      await ctx.send(f"For <{ctx.author.name}>:\n\nuh-oh! Activity was cancelled due to long time no response. See you next time!")
      return
   
   await ctx.send(f"For <{ctx.author.name}>:\n\nPlease wait a moment while we fetch your suggestions...")

   # send suggestions and wait for user's reaction to suggestion
   # sugg_list contains indices of the suggestions with highest mab scores:
   sugg_list = mab_instance.recommend(RECO_SIZE, context_index, mab_instance.is_first_time(context_index, RECO_SIZE))
   message = "Please type in the chat with the number of your choice:"
   for i, sugg_idx in enumerate(sugg_list, start = 1):
      message += f"\n{i}. {SUGGESTIONS[sugg_idx]}"
   await ctx.send(message)
   
   try:
      while True:
         suggestion_response = await bot.wait_for('message', check=check, timeout=60)
         try: 
            # this index is a temporary index in the sugg_list, we need to get the actual index later for the picked suggestion in SUGGESTIONS:
            sugg_idx_temp = int(suggestion_response.content) - 1
            if 0 <= sugg_idx_temp < len(sugg_list):
               break
            else:
               await ctx.send(f"For <{ctx.author.name}>:\n\nInvalid activity selection. Please enter a valid number.")
         except ValueError:
            await ctx.send(f"For <{ctx.author.name}>:\n\nInvalid input. Please enter numbers only.")
   except asyncio.TimeoutError:
      await ctx.send(f"For <{ctx.author.name}>:\n\nuh-oh! Activity was cancelled due to long time no response. See you next time!")
      return

   # Get the real suggestion index:
   suggestion_index = sugg_list[sugg_idx_temp]

   # send detailed instructions for action:
   await ctx.send(f"For <{ctx.author.name}>:\n\nGreat! {SUGG_INSTRUCT_DICT[SUGGESTIONS[suggestion_index]]}")

   # get user feedback for this activity:
   message = f"For <{ctx.author.name}>:\n\nTake your time! Once you are done, please provide a feedback from 0 (unhelpful) to 5 (out of this world) so we can better help you next time!"
   await ctx.send(message)
   
   try:
      while True:
         feedback_response = await bot.wait_for('message', check=check, timeout=1200)
         try:
            feedback_rating = int(feedback_response.content)
            if 0 <= feedback_rating <= 5:
               break
            else:
               await ctx.send(f"For <{ctx.author.name}>:\n\nInvalid feedback. Please enter a feedback from 0 ~ 5.")
         except ValueError:
            await ctx.send(f"For <{ctx.author.name}>:\n\nInvalid input. Please enter numbers only.")
   except asyncio.TimeoutError:
      await ctx.send(f"For <{ctx.author.name}>:\n\nuh-oh! Activity was cancelled due to long time no response. See you next time!")
      return
   
   await ctx.send(f"For <{ctx.author.name}>:\n\nExcellent! Hope you feel better after this activity! See you next time!")

   # update data & history data file:
   mab_instance.update(feedback_rating, suggestion_index, context_index)
   mab_instance.write_hist_file(HISTORY_DATA_FILE)

   # update activity in both user's own activity history, and the total activity history
   curr_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
   activity_entry = f"[{curr_time}]\t{ctx.author.name} <{ctx.author.id}>: Context: [{CONTEXTS[context_index]}], Selection: [{SUGGESTIONS[suggestion_index]}], Feedback: [{feedback_rating}].\n"
   mab_instance.update_activity_log(f"{ctx.author.id}_activity.txt", activity_entry)
   mab_instance.update_activity_log("total_activity.txt", activity_entry)

# Run the bot:
bot.run(BOT_TOKEN)