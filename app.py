from sql import connection
import os
from dotenv import load_dotenv
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes, Updater, CallbackQueryHandler
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


## Dictionary for the languages
messages = {
    "ita": {
        "welcome": "Benvenutə!",
        "language_selected": "Lingua italiana impostata, benvenutə!",
    },
    "eng": {
        "welcome": "Welcome!",
        "language_selected": "English language selected, welcome!",
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
    
## The following code will be executed when the bot receives a callback query (change language)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global user_language
    query = update.callback_query
    await query.answer()

    user_language = get_user_language(query.data)
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text=messages[user_language]["language_selected"])

## The following code will be executed when the bot receives an unkown command

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

## Format Articles function

def format_articles(articles):
    # Initialize an empty string to build the message
    formatted_message = ""

    # Loop through each article in the list
    for article in articles:
        # Assume that the articles have 'title' and 'content' fields'
        title = article.get('link', 'Titolo non disponibile')
        content = article.get('descrizione_link', 'Contenuto non disponibile')
        
        # Add each article to the formatted message
        formatted_message += f"📌 *{title}*\n"
        formatted_message += f"{content[:100]}...\n"  # Mostra i primi 100 caratteri del contenuto
        formatted_message += "\n"

    # If there are no articles, return a default message
    return formatted_message if formatted_message else "Nessun articolo trovato."


## The following function retrieves articles and link from the database

def get_articles():
    if connection:
        try:
            with connection.cursor() as cursor:
                # Query to select articles from the table, modify link_utili with the correct table name
                sql_query = "SELECT * FROM link_utili"
                cursor.execute(sql_query)
                # Retrieve all results of the query
                results = cursor.fetchall()
                return results
        except MySQLError as e:
            logging.error(f"Errore nell'esecuzione della query: {e}")
            return None
        # The connection remains open as it is global in the sql.py module; do not close it here
    else:
        return None
    
# Handler for the /articles command
async def articles(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Call the function that retrieves the articles from the database
    articles = get_articles()
    
    if articles:
        # Format the message with the results
        formatted_message = format_articles(articles)
    else:
        # If there are no articles or there was an error, send an error message
        formatted_message = "Non è stato possibile recuperare gli articoli."

    # Send the message with the articles to the user
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=formatted_message, 
        parse_mode='Markdown'  # Use Markdown to format the article titles in bold
    )

## The following code will be executed when the bot receives a message

if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_API).build()

    start_handler = CommandHandler('start', start)
    articles_handler = CommandHandler('articles', articles)
    button_handler = CallbackQueryHandler(button)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)


    application.add_handler(start_handler)
    application.add_handler(button_handler)
    application.add_handler(articles_handler)
    application.add_handler(unknown_handler)
    
    application.run_polling()