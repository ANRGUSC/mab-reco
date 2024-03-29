# This is the main program to activate the telegram bot, to change the bot with your own bot, simply change the telegram bot
# token and telegram bot username in the .env file. For more details, please ask for chatGPT and visit online tutorials.

# For test run or run this in a docker image, please take a look at the docker-compose.yml or docker-compose-swarm.yml

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters, CallbackContext, ContextTypes
import os
from dotenv import load_dotenv
import datetime
import pytz
import numpy as np
from MABInstance import MABInstance

# Get bot token:
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BOT_USERNAME = os.getenv("TELEGRAM_BOT_USERNAME")

# /start command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
   await update.message.reply_text('Hello! I am your stress relief assistant.\n\nType "/" to see what command options you have.\n\nType "/help" to view more.')

# /help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
   await update.message.reply_text('Type "/suggest" for me to provide with you stress relief activities.\n\nType "/cancel" to terminate the current suggestion process.')

# ---------------------------------------------------------------------------------------------------------------------------
# /suggest command
# define states (can think states as different parts of the whole user interaction)
SELECT_CONTEXT, SELECT_SUGGESTION, COLLECT_FEEDBACK = range(3)

# start /suggest command, ask user about what context they are in and proceed to the next screen with suggestions:
async def start_suggestion(update: Update, context: CallbackContext):
   user = update.message.from_user
   user_hash_code = user.id

   # initialize mab instance:
   mab_instance = MABInstance(user_hash_code, True, "telegram")
   context.user_data['mab_instance'] = mab_instance

   # get context and send message:
   contexts = mab_instance.get_contexts()
   message = f"Hello, {user.first_name}! Which of the following scenario are you in right now:\n"
   for i, context in enumerate(contexts, start = 1):
      message += f"\n{i}. {context}\n"
   message += "\nType in the chat with the number of your choice."
   await update.message.reply_text(message)

   return SELECT_CONTEXT

# /suggest command: get context offer first list suggestions
async def select_context(update: Update, context: CallbackContext) -> int:
   # get mab instance
   mab_instance = context.user_data['mab_instance']
   contexts = mab_instance.get_contexts()
   
   # get context:
   context_response = update.message.text.strip()
   try:
      context_index = int(context_response) - 1
      if context_index < 0 or context_index >= len(contexts):
         raise ValueError()
   except ValueError:
      if context_response == "/suggest":
         await update.message.reply_text('The current recommendation process is not finished yet. If you wish to start a new one, please call "/cancel" first before calling "/suggest".')
      elif context_response == "/cancel":
         await update.message.reply_text('The current recommendation process has been terminated. Feel free to start a new recommendation process by calling "/suggest" again.')
         return ConversationHandler.END
      else:
         await update.message.reply_text(f"Uh-oh...Please select a context with a number input from 1 ~ {len(contexts)}.")
      return SELECT_CONTEXT

   # offer first list of suggestions: (suppose for first round, there is always some suggestions)
   suggestions = mab_instance.get_suggestions()
   sugg_list = mab_instance.make_recommendation(context_index)
   prev_sugg_indices = np.where(np.isin(suggestions, sugg_list))[0] # suggestion indices
   message = "Please wait a moment while we fetch your suggestions..."
   message += "\n\nYay! Here they are. Choose what you want to do most right now.\n\nIf you don't like any of the recommendations, simply reply 0.\n"
   for i, sugg in enumerate(sugg_list, start = 1):
      message += f"\n{i}. {sugg}\n"
   await update.message.reply_text(message)

   # store information for next state:
   context.user_data['context_index'] = context_index
   context.user_data['prev_sugg_indices'] = prev_sugg_indices
   context.user_data['sugg_list'] = sugg_list

   return SELECT_SUGGESTION

# /suggest command: get suggestion:
async def select_suggestion(update: Update, context: CallbackContext) -> int:
   # get info:
   mab_instance = context.user_data['mab_instance']
   context_index = context.user_data['context_index']
   prev_sugg_indices = context.user_data['prev_sugg_indices']
   sugg_list = context.user_data['sugg_list']
   suggestions = mab_instance.get_suggestions()

   # get user response:
   suggestion_response = update.message.text.strip()
   try:
      sugg_idx = int(suggestion_response) - 1
      if sugg_idx < -1 or sugg_idx >= len(sugg_list):
         raise ValueError()
   except ValueError:
      if suggestion_response == "/suggest":
         await update.message.reply_text('The current recommendation process is not finished yet. If you wish to start a new one, please call "/cancel" first before calling "/suggest".')
      elif suggestion_response == "/cancel":
         await update.message.reply_text('The current recommendation process has been terminated. Feel free to start a new recommendation process by calling "/suggest" again.')
         return ConversationHandler.END
      else:
         await update.message.reply_text(f"Uh-oh...Please select an activity with a number input from 0 ~ {len(sugg_list)}.")
      return SELECT_SUGGESTION

   if sugg_idx == -1:
      sugg_list = mab_instance.make_recommendation(context_index, prev_sugg_indices)
      context.user_data['sugg_list'] = sugg_list
      # if no more suggestions left, we end in here:
      if len(sugg_list) == 0:
         await update.message.reply_text("Oops... Looks like you didn't like all the activities we just gave you.\n\nWe will add more options, please come back next time!")
         feedback_rating = -1
         suggestion_index = -1
         mab_instance.update_mab_file(context_index, suggestion_index, feedback_rating, prev_sugg_indices)
         # close database connection:
         mab_instance.close_db_connection()
         return ConversationHandler.END
      else:
         # show new list of suggestions:
         message = "Don't worry! Let's try this again, One moment please..."
         message += "\n\nYay! Here they are. Choose what you want to do most right now.\n\nIf you don't like any of the recommendations, simply reply 0.\n"
         for i, sugg in enumerate(sugg_list, start = 1):
            message += f"\n{i}. {sugg}\n"
         await update.message.reply_text(message)
         # update prev sugg indices
         sugg_indices = np.where(np.isin(suggestions, sugg_list))[0]
         prev_sugg_indices = np.unique(np.concatenate((prev_sugg_indices, sugg_indices)).astype(int))
         context.user_data['prev_sugg_indices'] = prev_sugg_indices
         return SELECT_SUGGESTION

   # after a valid suggestion is picked, we get in here, get real suggestion index:
   suggestion_index = mab_instance.get_suggestion_index(sugg_list[sugg_idx])

   # store and update data:
   context.user_data['suggestion_index'] = suggestion_index
   context.user_data['prev_sugg_indices'] = prev_sugg_indices
      
   # gives suggestion detail and image:
   await update.message.reply_photo(photo=mab_instance.get_suggestion_Image(suggestion_index))
   message = f"Great! {mab_instance.get_suggestion_description(suggestion_index)}"
   message += "\n\nTake your time! Once you are done, please provide a feedback from 0 (unhelpful) to 5 (out of this world) so we can better help you next time!"
   await update.message.reply_text(message)
   
   return COLLECT_FEEDBACK

# /suggest command: offer suggestion details and get feedback and update
async def collect_feedback(update: Update, context: CallbackContext) -> int:
   mab_instance = context.user_data['mab_instance']
   context_index = context.user_data['context_index']
   suggestion_index = context.user_data['suggestion_index']
   prev_sugg_indices = context.user_data['prev_sugg_indices']
   
   feedback_response = update.message.text.strip()
   try:
      feedback_rating = int(feedback_response)
      if feedback_rating < 0 or feedback_rating > 5:
         raise ValueError()        
   except ValueError:
      if feedback_response == "/suggest":
         await update.message.reply_text('The current recommendation process is not finished yet. If you wish to start a new one, please call "/cancel" first before calling "/suggest".')
      elif feedback_response == "/cancel":
         await update.message.reply_text('The current recommendation process has been terminated. Feel free to start a new recommendation process by calling "/suggest" again.')
         return ConversationHandler.END
      else:
         await update.message.reply_text("Uh-oh...Please provide a feedback with a number input from 0 ~ 5.")
      return COLLECT_FEEDBACK
   
   # last message:
   if feedback_rating == 0:
      await update.message.reply_text("Uh-oh... I'm sorry this activity isn't helpful to you. We will add more activities. Thank you for your time and patience.")
   elif feedback_rating <= 3:
      await update.message.reply_text("That's great! I'm glad you tried our activity. We will make further improvements. Until next time!")
   else:
      await update.message.reply_text("Excellent! I'm glad our activity helped. Have a nice day!")
   
   # update activity in both user's own activity history, and the total activity history
   utc_now = datetime.datetime.utcnow()
   pacific = pytz.timezone('US/Pacific')
   pdt_now = pacific.fromutc(utc_now)
   curr_time = pdt_now.strftime("%Y-%m-%d %H:%M:%S")
   mab_instance.update_activity_log(curr_time, context_index, suggestion_index, feedback_rating)
   
   # update mab data files:
   mab_instance.update_mab_file(context_index, suggestion_index, feedback_rating, prev_sugg_indices)
   # close database connection:
   mab_instance.close_db_connection()
   # end command:
   return ConversationHandler.END
# ---------------------------------------------------------------------------------------------------------------------------

# cancel suggest command:
async def cancel(update: Update, context: CallbackContext) -> int:
   await update.message.reply_text('The current recommendation process has been terminated. Feel free to start a new recommendation process by calling "/suggest" again.')
   return ConversationHandler.END

# error handler:
async def error_handler(update: Update, context: CallbackContext):
   print(f'Update {update} caused error {context.error}')
   await update.message.reply_text("An error occurred while processing your request. Please try again later.")

# MAIN
def main():
   app = Application.builder().token(BOT_TOKEN).build()

   # commands
   app.add_handler(CommandHandler('start', start_command))
   app.add_handler(CommandHandler('help', help_command))

   # create a conversation handler for /suggest command:
   suggest_conversation_handler = ConversationHandler(
      entry_points=[CommandHandler('suggest', start_suggestion)],
      states={
         SELECT_CONTEXT: [MessageHandler(filters.TEXT, select_context)],
         SELECT_SUGGESTION: [MessageHandler(filters.TEXT, select_suggestion)],
         COLLECT_FEEDBACK: [MessageHandler(filters.TEXT, collect_feedback)]
      },
      fallbacks=[CommandHandler('cancel', cancel)]
   )
   app.add_handler(suggest_conversation_handler)

   # add the error handler:
   app.add_error_handler(error_handler)

   # start it:
   app.run_polling(poll_interval=0.1)

if __name__ == '__main__':
   main()