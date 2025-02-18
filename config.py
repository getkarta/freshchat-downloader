import os
from dotenv import load_dotenv

# Load environment variables from the .env file.
load_dotenv()

# Configuration variables fetched from the .env file.
FRESHCHAT_ACCOUNT_URL = os.getenv("FRESHCHAT_ACCOUNT_URL")
FRESHCHAT_API_KEY = os.getenv("FRESHCHAT_API_KEY")

if not FRESHCHAT_ACCOUNT_URL or not FRESHCHAT_API_KEY:
    raise ValueError("Please set FRESHCHAT_ACCOUNT_URL and FRESHCHAT_API_KEY in your .env file") 