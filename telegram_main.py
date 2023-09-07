from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
from dotenv import load_dotenv
import datetime
import numpy as np
from MABInstance import MABInstance

# Get bot token:
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BOT_USERNAME = os.getenv("TELEGRAM_BOT_USERNAME")

# /start command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
   await update.message.reply_text("Hello! I am your stress relief assistant.")

# /help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
   await update.message.reply_text("Please type \"suggest for me to provide with you stress relief activities :D")

async def suggest_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
   await update.message.reply_text("Please type \"suggest for me to provide with you stress relief activities :D")

# Responses
def handle_response(text):
   text = text.lower()
   if 'hello' in text:
      return "Hello!"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
   message_type = update.message.chat.type
   text = update.message.text
   print(f'User {update.message.chat.id} in {message_type}: {text}')

   if message_type == 'group':
      if BOT_USERNAME in text:
         new_text = text.replace(BOT_USERNAME, '').strip()
         response = handle_response(new_text)
   else:
      response = handle_response(new_text)

   await update.message.reply_text(response)
   

if __name__ == '__main__':
   print("Running...")
   app = Application.builder().token(BOT_TOKEN).build()

   # Commands
   app.add_handler(CommandHandler('start', start_command))
   app.add_handler(CommandHandler('help', help_command))
   app.add_handler(CommandHandler('suggest', suggest_command))

   # Messages
   app.add_error_handler(MessageHandler(filters.TEXT, handle_message))

   # Polls the bot
   print("Polling...")
   app.run_polling(poll_interval=1)