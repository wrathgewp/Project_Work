import os
from dotenv import load_dotenv
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes, Updater, CallbackQueryHandler
import pymysql
from pymysql.err import MySQLError
import sql
from sql import get_dizionario

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


## Dictionary for the languages
messages = {
    "ita": {
        "welcome": "Benvenutə!",
        "language_selected": " 🇮🇹 Lingua italiana impostata, benvenutə!",
        "functionalities": "Ciao questo bot può aiutarti nelle seguenti cose: \n\n"
        "1️⃣ Puoi cercare una parola che non ti è comprensibile nel tuo contratto e ti dirà la sua definizione; \n\n"
        "2️⃣ Ti dirà i sindacati e i patronati localizzati a Verona e nella sua provincia; \n\n"
        "3️⃣ Ti mette a disposizione articoli e link utili per aiutarti a risolvere i tuoi dubbi!",
    },
    "eng": {
        "welcome": "Welcome!",
        "language_selected": " 🇬🇧 English language selected, welcome!",
        "functionalities": "Hello this bot can help you with the following things: \n\n"
        "1️⃣ You can search for a word that you don't understand in your contract and it will tell you its definition; \n\n"
        "2️⃣ It will tell you the unions and patronages located in Verona and in its province; \n\n"
        "3️⃣ It will put at your disposal articles and links to help you solve your doubts!",
    }
}

## Function to get the user language

def get_user_language(language_code):
    return "ita" if language_code == "ita" else "eng"

## The following code activate logging to allow debugging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

user_language = "eng" ##Default language

## The following code will be executed when the bot is started

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ## Buttons creation
    ita = InlineKeyboardButton("🇮🇹", callback_data='ita')
    eng = InlineKeyboardButton("🇬🇧", callback_data='eng')
    
    ## InlineKeyboardMarkup creation
    keyboard = [[ita, eng]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=messages[user_language]["welcome"], 
        reply_markup=reply_markup
    )
    
## The following code will be executed when the bot receives a callback query

async def language_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global user_language
    query = update.callback_query
    await query.answer()

    user_language = get_user_language(query.data)
    dictionary = get_dizionario(user_language)
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text=messages[user_language]["language_selected"])
    
    await functionalities_keyboard(update, context)
    
    return dictionary

## The following code will be executed when the bot receives a message
async def functionalities_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    words_btn = InlineKeyboardButton("🔎", callback_data='words')
    unions_btn = InlineKeyboardButton("👥", callback_data='unions')
    links_btn = InlineKeyboardButton("🔗", callback_data='link')
    keyboard_btn = [[words_btn, unions_btn, links_btn]]
    reply_markup = InlineKeyboardMarkup(keyboard_btn)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=messages[user_language]["functionalities"],
        reply_markup=reply_markup
    )
    
## The following code will be executed when the bot receives an unkown command

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

## The following code will be executed when the bot receives a message

if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_API).build()

    start_handler = CommandHandler('start', start)
    button_handler = CallbackQueryHandler(language_button)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)

    application.add_handler(start_handler)
    application.add_handler(button_handler)
    application.add_handler(unknown_handler)
    
    application.run_polling()