from sql import connection
import os
from dotenv import load_dotenv
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes, Updater, CallbackQueryHandler
import pymysql
import sql
from sql import get_articles
from sql import get_syndicates
#from sql import get_syndicates_by_comune
from sql import get_available_comuni

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
    },
    "eng": {
        "welcome": "Welcome! Please select your language.",
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
    ita = InlineKeyboardButton("🇮🇹", callback_data='lang_ita')
    eng = InlineKeyboardButton("🇬🇧", callback_data='lang_eng')    
    ## InlineKeyboardMarkup creation
    keyboard = [[ita, eng]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=messages[user_language]["welcome"], 
        reply_markup=reply_markup
    )
    
## Function to handle language selection

async def language_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global user_language
    query = update.callback_query
    await query.answer()
    if query.data.startswith("lang_"):
        user_language = get_user_language(query.data.split("_")[1])
        await context.bot.send_message(chat_id=update.effective_chat.id, text=messages[user_language]["language_selected"])
        await functionalities_keyboard(update, context)
    else: 
        return
## The following code is a function that display the functionalities keyboard

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
      
## Function to handle "links" button
async def links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()    
    if query.data == 'links':
        await articles(update, context)
    else: 
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Altri pulsanti non implementati ancora.")

## Function to format articles
def format_articles(articles):
    # Initialize an empty string to build the message
    formatted_message = ""

    # Loop through each article in the list
    for article in articles:
        # Assume that the articles have 'title' and 'content' fields'
        link = article.get('link', 'link non disponibile')
        formatted_message += f"🔗 [{link}]({link})\n\n"
    # If there are no articles, return a default message
    return formatted_message if formatted_message else "Nessun articolo trovato."

 
# Handler for articles button
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

## The following code will be executed when the bot receives an unkown command

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

## The following code will be executed when a file is uploaded by a user

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

# Handler per il comando /comuni
async def comuni(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Recupera l'elenco dei comuni dal database
    comuni = get_available_comuni()

    if comuni:
        # Crea i pulsanti per ciascun comune
        keyboard = [
            [InlineKeyboardButton(comune, callback_data=comune)] for comune in comuni
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Invia il messaggio con la tastiera
        await update.message.reply_text("Seleziona il comune:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("Nessun comune disponibile.")


# Handler per gestire la selezione del comune
async def select_comune(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    comune_selezionato = query.data  # Questo è il comune selezionato dall'utente
    await query.answer()  # Rispondi al callback

    # Recupera i sindacati per il comune selezionato
    sindacati = sql.get_syndicates_by_comune(comune_selezionato)

    if sindacati:
        formatted_message = format_syndicates(sindacati)
    else:
        formatted_message = f"Nessun sindacato trovato per {comune_selezionato}."

    # Invia i risultati filtrati
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=formatted_message,
        parse_mode='Markdown'
    )


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



## The following code will be executed when the bot receives a message

if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_API).build()

    start_handler = CommandHandler('start', start)
    syndicates_handler = CommandHandler('syndicates', syndicates)  # Nuovo handler per /syndicates
    comuni_handler = CommandHandler('comuni', comuni)
    select_comune_handler = CallbackQueryHandler(select_comune)
    button_handler = CallbackQueryHandler(language_button, pattern='^lang_')
    functionalities_handler = CallbackQueryHandler(links, pattern='^(words|unions|links)$')
    unknown_handler = MessageHandler(filters.COMMAND, unknown)


    application.add_handler(start_handler)
    application.add_handler(syndicates_handler)  # Aggiungi l'handler qui
    application.add_handler(button_handler)
    application.add_handler(comuni_handler)
    application.add_handler(select_comune_handler)
    application.add_handler(functionalities_handler)
    application.add_handler(unknown_handler)
    
    application.run_polling()