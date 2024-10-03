from functools import wraps
from multiprocessing import connection
import os
from dotenv import load_dotenv
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes, Updater, CallbackQueryHandler
from pymysql import MySQLError
import sql
from sql import *
import re
from fuzzywuzzy import fuzz
import string
import pymupdf

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
        "syndicates": "Ecco i sindacati disponibili nel comune di ",
        "name":  "Nome",
        "address": "Indirizzo",
        "phone": "Telefono",
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
        "syndicates": "Here are the syndicates available in the city of ",
        "name":  "Name",
        "address": "Address",
        "phone": "Phone",
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
    #upload_btn = InlineKeyboardButton("📄", callback_data='upload')
    #keyboard_btn = [[words_btn, unions_btn, links_btn, upload_btn]]
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
    elif query.data == 'words':
        await word_definition(update, context)
    elif query.data == 'unions':
            await comuni(update, context)
    else: 
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Altri pulsanti non implementati ancora.")

## Function to format articles
def format_articles(articles):
    formatted = messages[user_language]["intro_articles"]
    for article in articles:
        formatted += f"🔗 {article['link']}\n\n"
    return formatted


@load_language
async def articles(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    articles_data = sql.get_articles()
    if articles_data:
        formatted_message = format_articles(articles_data)
        if update.message:
            await update.message.reply_text(formatted_message)
        elif update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.message.reply_text(formatted_message)
    else:
        if update.message:
            await update.message.reply_text("No articles found.")
        elif update.callback_query:
            await update.callback_query.answer("No articles found.")

## Functions for document upload and processing

# This function splits messages if they are too long
def split_message(message, max_length=4096):
    return [message[i:i+max_length] for i in range(0, len(message), max_length)]

# This function handles longer messages
async def send_long_message(chat_id, text, context):
    parts = split_message(text)
    for part in parts:
        await context.bot.send_message(chat_id=chat_id, text=part, parse_mode='Markdown')

# Function to extract text from a PDF file
def extract_text_from_pdf(pdf_path):
    text = ""
    with pymupdf.open(pdf_path) as pdf_document:
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            text += page.get_text("text")  # Extract the text from each page
    return text

    
## The following code will be executed when the bot receives an unkown command

@load_language
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=messages[user_language]["nocommand"])



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
    

# Handler per il comando /comuni
async def comuni(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    available_comuni = sql.get_available_comuni()
    keyboard = [[InlineKeyboardButton(comune, callback_data=f"comune:{comune}")] for comune in available_comuni]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text("Seleziona il comune:", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.reply_text("Seleziona il comune:", reply_markup=reply_markup)



async def select_comune(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    comune_selezionato = query.data.split(':')[1]
    
    sindacati = sql.get_syndicates_by_comune(comune_selezionato)
    
    if sindacati:
        message = f"{messages[user_language]['syndicates']} {comune_selezionato}:\n\n"
        for sindacato in sindacati:
            message += f"{messages[user_language]['name']}: {sindacato.get('nome', 'N/A')}\n"
            message += f"{messages[user_language]['address']}: {sindacato.get('indirizzo', 'N/A')}\n"
            message += f"{messages[user_language]['phone']}: {sindacato.get('telefono', 'N/A')}\n\n"
        
        await query.answer()
        await query.message.reply_text(message)
    else:
        await query.answer(f"Nessun sindacato trovato per {comune_selezionato}")




def format_syndicates(syndicates):
    # Inizializza una stringa vuota per costruire il messaggio
    formatted_message = ""

    # Loop attraverso ogni sindacato nella lista
    for syndicate in syndicates:
        nome = syndicate.get('nome', 'Nome non disponibile')
        indirizzo = syndicate.get('indirizzo', 'Indirizzo non disponibile')
        cap = syndicate.get('cap', 'CAP non disponibile')
        comune = syndicate.get('comune', 'Comune non disponibile')
        num_telefono = syndicate.get('num_telefono', 'Numero di telefono non disponibile')
        email = syndicate.get('email', 'Email non disponibile')
        sito = syndicate.get('sito', 'Sito web non disponibile')

        # Aggiungi le informazioni del sindacato al messaggio formattato
        formatted_message += f"📌 *{nome}*\n"
        formatted_message += f"📍 Indirizzo: {indirizzo}, {cap}, {comune}\n"
        formatted_message += f"📞 Telefono: +39{num_telefono}\n"
        formatted_message += f"✉️ Email: {email}\n"
        formatted_message += f"🌐 Sito: {sito}\n"
        formatted_message += "\n"

    # Se non ci sono sindacati, ritorna un messaggio predefinito
    return formatted_message if formatted_message else "Nessun sindacato trovato."


# Handler per il comando /syndicates
async def syndicates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Chiamata alla funzione che prende i sindacati dal database
    syndicates = get_syndicates()

    if syndicates:
        # Formatta il messaggio con i risultati
        formatted_message = format_syndicates(syndicates)
    else:
        # Se non ci sono sindacati o c'è stato un errore, invia un messaggio d'errore
        formatted_message = "Non è stato possibile recuperare i sindacati."

    # Invia il messaggio con i sindacati all'utente
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=formatted_message,
        parse_mode='Markdown'  # Usa il Markdown per formattare il messaggio
    )


## The following code will be executed when a file is uploaded by a user

## Functions for document upload and processing

## This function tokenizes the text word for word
def tokenize_text(text):
    tokens = re.findall(r'\b\w+\b', text.lower())
    return tokens

## This functions searches if terms that are in our database are also present in the document
def find_matches_in_db(tokens, dizionario):
    matching_terms = set()  # Use a set to avoid duplicates

    # Normalize the terms in the database
    normalized_terms = [(term.lower(), definition) for term, definition in dizionario]

    for token in tokens:
        if len(token) > 4:  # Ensure the token is long enough to modify
            modified_token = token[:-1]  # Remove the last two letters
        else:
            continue  # Skip tokens that are too short

        # Ensure modified token is at least 3 characters long
        if len(modified_token) < 4:
            continue

        # Check if the modified token is contained in any term
        for termine, definizione in normalized_terms:
            if modified_token in termine:
                print(f"Found match: '{modified_token}' in term: '{termine}'")  # Debug output
                matching_terms.add((termine, definizione))  # Append the term and its definition
                break  # Exit the loop once a match is found

    return list(matching_terms)  # Convert the set back to a list for returning



def process_file(file_path, connection):
    # Fetch the terms and definitions from the database
    database_terms = sql.get_word_definition()  # This should return a list of (term, definition) tuples
    
    # Check file extension to determine if it's a .txt or .pdf file
    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension == '.txt':
        # Read the content of the text file
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
    elif file_extension == '.pdf':
        # Extract text from the PDF file
        text = extract_text_from_pdf(file_path)
    else:
        raise ValueError("Unsupported file format. Please upload a .txt or .pdf file.")


    # Basic text cleaning (removing punctuation and converting to lowercase)
    cleaned_text = text.translate(str.maketrans('', '', string.punctuation)).lower()

    # Tokenize the cleaned text
    tokens_in_file = tokenize_text(cleaned_text)

    # Debug: Print the tokens found in the file
    print(f"Tokens from file: {tokens_in_file}")

    # Find matching terms in the database
    matching_terms = find_matches_in_db(tokens_in_file, database_terms)

    # Debug: Print the matching terms found
    print(f"Matching terms found: {matching_terms}")

    return matching_terms


# The following code will be executed when a file is uploaded by a user
async def upload_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    # Check if the user has initiated the upload process with the /upload command
    if not context.user_data.get('upload_ready', False):
        await update.message.reply_text("Please use the /upload command before sending a document.")
        return

    document = update.message.document

    if document is not None:
        file_id = document.file_id

        # Get the file from Telegram servers
        file = await context.bot.get_file(file_id)

        # Directory where files will be saved
        download_dir = "/home/andrea/Desktop/pw_ifts/download_test"  
        file_path = os.path.join(download_dir, document.file_name)

        # Download the file to the directory
        await file.download_to_drive(file_path)

        await update.message.reply_text(f"File '{document.file_name}' received and downloaded. Processing...")

        try:
            # Process the file and search for matching terms in the user's language
            matching_terms = process_file(file_path, connection)

            if matching_terms:
                # Prepare the message with found terms
                result_message = "Found terms:\n\n"
                for term, definition in matching_terms:
                    result_message += f"- {term}: {definition} \n"
            else:
                result_message = "No matching terms found in the document."

            # Split and send the message if it's too long
            messages = split_message(result_message)
            for msg in messages:
                await update.message.reply_text(msg)

        except Exception as e:
            logging.error(f"Error during file processing: {e}")
            await update.message.reply_text("An error occurred during file processing.")
        
        finally:
            # Remove the file after processing for privacy reasons
            delete_file(file_path)


async def upload_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Set a flag in user_data indicating the user is ready to upload a document
    context.user_data['upload_ready'] = True
    await update.message.reply_text("Please upload your document now.")


## This function is used to delete a file 
def delete_file(file_path):
    try:
        os.remove(file_path)
    except OSError as e:
        logging.error(f"Errore durante la cancellazione del file: {e}")



## The following code will be executed when the bot receives a message


if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_API).build()

    start_handler = CommandHandler('start', start)
    syndicates_handler = CommandHandler('syndicates', syndicates)  # Nuovo handler per /syndicates
    comuni_handler = CommandHandler('comuni', comuni)
    button_handler = CallbackQueryHandler(language_button, pattern='^lang_')
    select_comune_handler = CallbackQueryHandler(select_comune)
    functionalities_handler = CallbackQueryHandler(links, pattern='^(words|unions|links|upload)$')
    word_definition_handler = CommandHandler('word_definition', word_definition)
    upload_handler = CommandHandler('upload', upload_command)
    file_upload_handler = MessageHandler(filters.Document.ALL, upload_document)
    word_input_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_word_input)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)


    application.add_handler(start_handler)
    application.add_handler(syndicates_handler)  # Aggiungi l'handler qui
    application.add_handler(button_handler)
    application.add_handler(comuni_handler)
    application.add_handler(functionalities_handler)
    application.add_handler(select_comune_handler)
    application.add_handler(word_definition_handler)
    application.add_handler(word_input_handler)
    application.add_handler(CallbackQueryHandler(set_user_language))
    application.add_handler(upload_handler)
    application.add_handler(file_upload_handler)
    application.add_handler(unknown_handler)
    
    application.run_polling()