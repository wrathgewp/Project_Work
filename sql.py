import pymysql.cursors
import os
from dotenv import load_dotenv

load_dotenv()
BOT_API = os.environ["BOT_API"]
HOST_DB = os.environ["HOST_DB"]
USER_DB = os.environ["USER_DB"]
PASSWORD_DB = os.environ["PASSWORD_DB"]
DATABASE = os.environ["DATABASE"]
PORT = os.environ["PORT"]

connection = pymysql.connect(host=HOST_DB,
                             user=USER_DB,
                             password=PASSWORD_DB,
                             database=DATABASE,
                             port=int(PORT),
                             cursorclass=pymysql.cursors.DictCursor)
        
def get_dizionario(language_code):
    table_name = f"dizionario_{language_code}"
    with connection.cursor() as cursor:
        query = f"SELECT * FROM {table_name}" 
        cursor.execute(query)
        result = cursor.fetchall()
        return result