import os
from dotenv import load_dotenv

print("Starting bot.")

if os.path.exists(".env"):

    print("Loading .env file.")

    load_dotenv()

    BOT_API = os.environ["BOT_API"]

elif "BOT_API" in os.environ:

    print("No .env file found, using environment variables.")

    BOT_API = os.environ["BOT_API"]

else:
    print('No .env file found, and no environment variables set. Extiting.')
    exit(1)

