import logging
import traceback
from pymysql import MySQLError
import pymysql.cursors
import os
from dotenv import load_dotenv

if os.path.exists(".env"):

    load_dotenv()
    HOST_DB = os.environ["HOST_DB"]
    USER_DB = os.environ["USER_DB"]
    PASSWORD_DB = os.environ["PASSWORD_DB"]
    DATABASE = os.environ["DATABASE"]
    PORT = os.environ["PORT"]

elif "HOST_DB" in os.environ:

    HOST_DB = os.environ["HOST_DB"]
    USER_DB = os.environ["USER_DB"]
    PASSWORD_DB = os.environ["PASSWORD_DB"]
    DATABASE = os.environ["DATABASE"]
    PORT = os.environ["PORT"]

else:
    print("No .env file found, and no environment variables set for database. Exiting.")
    exit(1)


connection = pymysql.connect(host=HOST_DB,
                             user=USER_DB,
                             password=PASSWORD_DB,
                             database=DATABASE,
                             port=int(PORT),
                             cursorclass=pymysql.cursors.DictCursor)

## The following function retrieves the definition of a word from the database
        
def get_word_definition(language_code, parola):
    table_name = f"dizionario_{language_code}"
    parola = f"%{parola}%"
    with connection.cursor() as cursor:
        query = f"SELECT parola, descrizione FROM {table_name} WHERE LOWER(parola) LIKE LOWER(%s)"
        cursor.execute(query, (parola,))
        result = cursor.fetchall()
        
        if result:
            return result
        else:
            return None

    
## The following function retrieves articles and link from the database

def get_articles():
    if connection:
        try:
            with connection.cursor() as cursor:
                # Query to select articles from the table, modify link_utili with the correct table name
                sql_query = "SELECT link FROM link_utili"
                cursor.execute(sql_query)
                # Retrieve all results of the query
                results = cursor.fetchall()
                return results if results else []
        except MySQLError as e:
            logging.error(f"Errore nell'esecuzione della query: {e}")
            logging.error(traceback.format_exc())
            return []
        # The connection remains open as it is global in the sql.py module; do not close it here
    else:
        logging.error("Connessione al database non disponibile.")
        return []

## The following function retrieves the user language from the database

def get_user_language(chat_id):
    with connection.cursor() as cursor:
        query = "SELECT lingua FROM lingua_utente WHERE chat_id = %s"
        cursor.execute(query, (chat_id,))
        result = cursor.fetchone()
        
        if result:
            return result['lingua']
        else:
            return 'eng'  # Default language if not found

## The following function saves the user language in the database

def save_user_language(chat_id, language):
    with connection.cursor() as cursor:
        query = "INSERT INTO lingua_utente (chat_id, lingua) VALUES (%s, %s) ON DUPLICATE KEY UPDATE lingua = %s"
        cursor.execute(query, (chat_id, language, language))
    connection.commit()

    

def get_syndicates():
    # Usa la connessione globale dal modulo sql.py
        if connection:
            try:
                with connection.cursor() as cursor:
                    # Query per selezionare i sindacati dalla tabella
                    sql_query = "SELECT * FROM sindacati"
                    cursor.execute(sql_query)
                    # Ottieni tutti i risultati della query
                    results = cursor.fetchall()
                    return results
            except MySQLError as e:
                logging.error(f"Errore nell'esecuzione della query: {e}")
                return None
        else:
            return None
        
def get_syndicates_by_comune(comune):
    if connection:
        try:
            with connection.cursor() as cursor:
                # Query per selezionare i sindacati filtrati per comune
                sql_query = "SELECT * FROM sindacati WHERE comune = %s"
                cursor.execute(sql_query, (comune,))
                results = cursor.fetchall()
                return results
        except MySQLError as e:
            logging.error(f"Errore nell'esecuzione della query: {e}")
            return []
        
# Funzione per recuperare i comuni disponibili
def get_available_comuni():
    if connection:
        try:
            with connection.cursor() as cursor:
                sql_query = "SELECT DISTINCT comune FROM sindacati"
                cursor.execute(sql_query)
                results = cursor.fetchall()
                return [row['comune'] for row in results]
        except MySQLError as e:
            logging.error(f"Errore nell'esecuzione della query: {e}")
            return []
