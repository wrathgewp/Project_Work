import logging
from pymysql import MySQLError
import pymysql.cursors
import os
from dotenv import load_dotenv

load_dotenv()
BOT_API = os.environ["BOT_API"]
HOST_DB = os.environ["HOST_DB"]
USER_DB = os.environ["USER_DB"]
PASSWORD_DB = os.environ["PASSWORD_DB"]
DATABASE = os.environ["DATABASE"]

connection = pymysql.connect(host=HOST_DB,
                             user=USER_DB,
                             password=PASSWORD_DB,
                             database=DATABASE,
                             cursorclass=pymysql.cursors.DictCursor)

## The following function retrieves the definition of a word from the database
        
""" def get_dizionario(language_code):
    table_name = f"dizionario_{language_code}"
    with connection.cursor() as cursor:
        query = f"SELECT parola, descrizione FROM {table_name} WHERE parola LIKE {parola}" 
        cursor.execute(query)
        result = cursor.fetchall()
        return result """
    
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
            return None
        # The connection remains open as it is global in the sql.py module; do not close it here
    else:
        return None