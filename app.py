import os
from dotenv import load_dotenv
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes, Updater, CallbackQueryHandler
import pymysql
import sql
from functools import wraps

# Inside a command or message handler

print("Starting bot.")

if os.path.exists(".env"):
    
    ## Check if the file .env exists

    print("Loading variables from .env file.")

    load_dotenv() ## Load the env file
 
    BOT_API = os.environ["BOT_API"] ## Set the BOT_API variable from the env file

elif "BOT_API" in os.environ:
    
    ## Check if the BOT_API variable is in the environment variables of the OS / Docker Image

    print("No .env file found, using environment variables.")

    BOT_API = os.environ["BOT_API"]

else:

    ## Exiting if the envronment variables are not set and there is no .env file
    
    print("No .env file found, and no environment variables set. Exiting.")

    exit(1) 


## ---------Telegram API code----------


## Dictionary for the languages
messages = {
    "ita": {
        "welcome": "Benvenutə! Seleziona la tua lingua.",
        "language_selected": " 🇮🇹 Lingua italiana impostata, benvenutə!",
        "functionalities": "Ciao questo bot può aiutarti nelle seguenti cose: \n\n"
        "1️⃣ Puoi cercare una parola che non ti è comprensibile nel tuo contratto e ti dirà la sua definizione; \n\n"
        "2️⃣ Ti dirà i sindacati e i patronati localizzati a Verona e nella sua provincia; \n\n"
        "3️⃣ Ti mette a disposizione articoli e link utili per aiutarti a risolvere i tuoi dubbi!",
        "word_definition_ask": "Inserisci la parola che vuoi cercare:",
        "meaning": "Ecco il significato della parola che hai inserito:\n\n",
        "no_word": "Non ho trovato nessuna parola che corrisponda a quella che hai inserito.",
        "nocommand": "Scusami, non ho capito il comando che hai inserito.",
        "intro_articles": "Ecco gli articoli disponibili: \n\n",
        "error_articles": "Articoli non disponibili",
    },
    "eng": {
        "welcome": "Welcome! Please select your language.",
        "language_selected": " 🇬🇧 English language selected, welcome!",
        "functionalities": "Hello this bot can help you with the following things: \n\n"
        "1️⃣ You can search for a word that you don't understand in your contract and it will tell you its definition; \n\n"
        "2️⃣ It will tell you the unions and patronages located in Verona and in its province; \n\n"
        "3️⃣ It will put at your disposal articles and links to help you solve your doubts!",
        "word_definition_ask": "Enter the word you want to search:",
        "meaning": "Here is the meaning of the word you entered:\n\n",
        "no_word": "I didn't find any word that matches the one you entered.",
        "nocommand": "Sorry, I didn't understand that command.",
        "intro_articles": "Here are the avaible artcles: \n\n",
        "error_articles": "Articles not available",
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

## The following code is a function that load the user language from database

async def set_user_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    lang = query.data.split('_')[1]
    sql.save_user_language(update.effective_chat.id, lang)
    context.user_data['language'] = lang
    await query.answer()


"""
    Decorator function that loads the user's language preference from the database and sets the `user_language` global variable before executing the decorated function.
    
    This decorator should be applied to any function that needs to access the user's language preference, such as functions that send messages to the user.
    
    Args:
        func (callable): The function to be decorated.
    
    Returns:
        callable: The decorated function that loads the user's language preference before execution.
    """
def load_language(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        global user_language
        user_language = sql.get_user_language(update.effective_chat.id)
        if not user_language:
            user_language = "ita"  # Default to Italian if no language is set
        return await func(update, context)
    return wrapper


## The following code will be executed when the bot is started

@load_language
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global user_language
    user_language = sql.get_user_language(update.effective_chat.id)
    
    # Buttons creation
    ita = InlineKeyboardButton("🇮🇹", callback_data='lang_ita')
    eng = InlineKeyboardButton("🇬🇧", callback_data='lang_eng')    
    # InlineKeyboardMarkup creation
    keyboard = [[ita, eng]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=messages[user_language]["welcome"], 
        reply_markup=reply_markup
    )
    
    
## Function to handle language selection

@load_language
async def language_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global user_language
    query = update.callback_query
    await query.answer()
    if query.data.startswith("lang_"):
        user_language = get_user_language(query.data.split("_")[1])
        
        # Save the language to the database
        sql.save_user_language(update.effective_chat.id, user_language)
        
        await context.bot.send_message(chat_id=update.effective_chat.id, text=messages[user_language]["language_selected"])
        await functionalities_keyboard(update, context)
    else: 
        return

## The following code is a function that display the functionalities keyboard

@load_language
async def functionalities_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    words_btn = InlineKeyboardButton("🔎", callback_data='words')
    unions_btn = InlineKeyboardButton("👥", callback_data='unions')
    links_btn = InlineKeyboardButton("🔗", callback_data='links')
    keyboard_btn = [[words_btn, unions_btn, links_btn]]
    reply_markup = InlineKeyboardMarkup(keyboard_btn)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=messages[user_language]["functionalities"],
        reply_markup=reply_markup
    )
      
@load_language
## Function to handle "links" button
async def links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()    
    if query.data == 'links':
        await articles(update, context)
    else: 
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Altri pulsanti non implementati ancora.")

@load_language
## Function to format articles
def format_articles(articles):
    if not articles:
        return messages[user_language]["error_articles"]
    
    text=messages[user_language]["intro_articles"] 
    # Loop through each article in the list
    for article in articles:
        # Assume that the articles have 'title' and 'content' fields'
        link = article.get('link', 'link non disponibile')
        text += f"🔗 [{link}]({link})\n\n"
    # If there are no articles, return a default message
    return text

@load_language
# Handler for articles button
async def articles(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Call the function that retrieves the articles from the database
    articles = sql.get_articles()
    
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


## Functions for document upload and processing

# Function to fetch terms from your database
def get_database_terms():
    if connection:
        try:
            with connection.cursor() as cursor:
                # Query to fetch terms from the definitions table
                cursor.execute("SELECT parola FROM dizionario_it")
                result = cursor.fetchall()
                # Fetch only the 'term' column
                return [row['parola'] for row in result]
        except MySQLError as e:
            logging.error(f"Errore nell'esecuzione della query: {e}")
            return None
    else:
        return none


# Load the spaCy English model
nlp = spacy.load('en_core_web_sm')  

# This function splits messages if they are too long
def split_message(message, max_length=4096):
    return [message[i:i+max_length] for i in range(0, len(message), max_length)]

# This function handles longer messages
async def send_long_message(chat_id, text, context):
    parts = split_message(text)
    for part in parts:
        await context.bot.send_message(chat_id=chat_id, text=part, parse_mode='Markdown')


## The following code will be executed when the bot receives an unkown command

@load_language
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=messages[user_language]["nocommand"])

## The following code will be executed when a file is uploaded by a user

@load_language
async def upload_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    document = update.message.document
    
    if document is not None:
        file_id = document.file_id
        
        # Get the file from Telegram servers
        file = await context.bot.get_file(file_id)
        
        # Directory where files will be saved in the container
        download_dir = "/app/downloads/"  # This path matches the container directory
        file_path = os.path.join(download_dir, document.file_name)
        
        # Download the file to the mapped volume
        await file.download_to_drive(file_path)
        
        await update.message.reply_text(f"File '{document.file_name}' received and downloaded. Processing...")
        
        # You can now process the file at file_path
        #process_file(file_path)
        
        # Optionally, remove the file after processing
        os.remove(file_path)


"""

Handles the /word_definition command
and the user's input of a word to get its definition.

When the /word_definition command is received,
the bot sends a message asking the user to send a word.
The `word_definition` function sets a flag in the user's data
to indicate that the bot is waiting for a word input.

When the user sends a word, the `handle_word_input` function checks
if the bot is waiting for a word input.
If so, it retrieves the definition of the word from the database
 and sends a message back to the user with the definition.

"""

@load_language
async def word_definition(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=messages[user_language]["word_definition_ask"])
    context.user_data['waiting_for_word'] = True

async def handle_word_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('waiting_for_word'):
        word = update.message.text
        definition = sql.get_word_definition(user_language, word)
        if definition and isinstance(definition, list):
            formatted_definition = "\n".join([f"{item['parola']}: {item['descrizione']}" for item in definition])
            message = messages[user_language]["meaning"] + formatted_definition
        else:
            message = messages[user_language]["no_word"]
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        context.user_data['waiting_for_word'] = False
    
## The following code will be executed when the bot receives a message


if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_API).build()

    start_handler = CommandHandler('start', start)
    button_handler = CallbackQueryHandler(language_button, pattern='^lang_')
    functionalities_handler = CallbackQueryHandler(links, pattern='^(words|unions|links)$')
    word_definition_handler = CommandHandler('word_definition', word_definition)
    word_input_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_word_input)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)


    application.add_handler(start_handler)
    application.add_handler(button_handler)
    application.add_handler(functionalities_handler)
    application.add_handler(word_definition_handler)
    application.add_handler(word_input_handler)
    application.add_handler(CallbackQueryHandler(set_user_language))
    application.add_handler(unknown_handler)
    
    application.run_polling()