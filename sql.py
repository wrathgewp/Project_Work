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
                return results
        except MySQLError as e:
            logging.error(f"Errore nell'esecuzione della query: {e}")
            logging.error(traceback.format_exc())
            return None
        # The connection remains open as it is global in the sql.py module; do not close it here
    else:
        logging.error("Connessione al database non disponibile.")
        return None

def get_dizionario(language_code):
    table_name = f"dizionario_{language_code}"
    with connection.cursor() as cursor:
        query = f"SELECT * FROM {table_name}" 
        cursor.execute(query)
        result = cursor.fetchall()
        return result