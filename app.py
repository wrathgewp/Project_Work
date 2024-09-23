import os
from dotenv import load_dotenv
import logging
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes
import pymysql
from pymysql.err import MySQLError
import sql

print("Starting bot.")

if os.path.exists(".env"):
    
    ## Check if the file .env exists

    print("Loading variables from .env file.")

    load_dotenv() ## Load the env file

    BOT_API = os.environ["BOT_API"] ## Set the BOT_API variable from the env file
    HOST_DB = os.environ["HOST_DB"]
    USER_DB = os.environ["USER_DB"]
    PASSWORD_DB = os.environ["PASSWORD_DB"]
    DATABASE = os.environ["DATABASE"]

elif "BOT_API" in os.environ and "HOST_DB" in os.environ and "USER_DB" in os.environ and "PASS_DB" in os.environ and "DB_NAME" in os.environ:
    
    ## Check if the BOT_API variable is in the environment variables of the OS / Docker Image

    print("No .env file found, using environment variables.")

    BOT_API = os.environ["BOT_API"]
    HOST_DB = os.environ["HOST_DB"]
    USER_DB = os.environ["USER_DB"]
    PASSWORD_DB = os.environ["PASSWORD_DB"]
    DATABASE = os.environ["DATABASE"]

else:

    ## Exiting if the envronment variables are not set and there is no .env file
    
    print("No .env file found, and no environment variables set. Exiting.")

    exit(1) 


## ---------Telegram API code----------

## The following code activate logging to allow debugging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

## The following code will be executed when the bot is started

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hi, i am the IFTS ProjectWork bot!")

## The following code will be executed when the bot receives an unkown command

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

## The following code will be executed when the bot receives a message

if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_API).build()

    start_handler = CommandHandler('start', start)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)

    application.add_handler(start_handler)
    application.add_handler(unknown_handler)
    
    application.run_polling()




    
