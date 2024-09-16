import os
from dotenv import load_dotenv

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

    ## Exiting if the BOT_API variable is not set and there is no .env file
    
    print("No .env file found, and no environment variables set. Exiting.")

    exit(1)

