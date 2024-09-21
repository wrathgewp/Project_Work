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

def prova():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM dizionario_it")
        result = cursor.fetchall()
        print (result)