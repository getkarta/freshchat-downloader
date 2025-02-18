import os
from dotenv import load_dotenv

# Load environment variables from the .env file.
load_dotenv()

# Configuration variables fetched from the .env file.
FRESHCHAT_ACCOUNT_URL = os.getenv("FRESHCHAT_ACCOUNT_URL")
FRESHCHAT_API_KEY = os.getenv("FRESHCHAT_API_KEY")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

if not FRESHCHAT_ACCOUNT_URL or not FRESHCHAT_API_KEY:
    raise ValueError("Please set FRESHCHAT_ACCOUNT_URL and FRESHCHAT_API_KEY in your .env file") 

if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
    raise ValueError("Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in your .env file") 