import os
import csv
import json
import logging
import time
import random
from config import FRESHCHAT_ACCOUNT_URL, FRESHCHAT_API_KEY
from freshchat_client import FreshchatClient
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define output directories and CSV file paths
OUTPUT_DIR = "output"
USERS_CSV = "users.csv"
CONV_CSV = "conversation_ids.csv"
CONVERSATIONS_DIR = "conversations"

def ensure_directories():
    """Create necessary directories if they don't exist"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, CONVERSATIONS_DIR), exist_ok=True)

def process_data():
    # Create necessary directories
    ensure_directories()

    # Initialize CSV files
    users_csv_path = os.path.join(OUTPUT_DIR, USERS_CSV)
    conv_csv_path = os.path.join(OUTPUT_DIR, CONV_CSV)

    # Store all conversation IDs and their corresponding user IDs
    all_conversations = []

    with open(users_csv_path, 'w', newline='') as users_file, \
         open(conv_csv_path, 'w', newline='') as conv_file:
        
        users_writer = csv.DictWriter(users_file, fieldnames=["user_id"])
        conv_writer = csv.DictWriter(conv_file, fieldnames=["user_id", "conversation_id"])
        users_writer.writeheader()
        conv_writer.writeheader()

        # Initialize Freshchat API client and fetch all users
        client = FreshchatClient(FRESHCHAT_ACCOUNT_URL, FRESHCHAT_API_KEY)
        logger.info("Fetching all users...")
        users = client.fetch_all_users()
        logger.info(f"Total users fetched: {len(users)}")

        # First pass: collect all user IDs and conversation IDs
        for user in users:
            user_id = user.get("id")
            if not user_id:
                logger.warning("User without id found, skipping.")
                continue

            # Record user id in the CSV
            users_writer.writerow({"user_id": user_id})
            logger.info(f"Processing user: {user_id}")

            try:
                conversations = client.get_user_conversations(user_id)
                logger.info(f"User {user_id} has {len(conversations)} conversation(s)")
                
                # Store conversation IDs with their user IDs
                for conv in conversations:
                    conv_id = conv.get("id") or conv.get("conversation_id")
                    if conv_id:
                        all_conversations.append({
                            "user_id": user_id,
                            "conversation_id": conv_id,
                            "conversation": conv
                        })
                        conv_writer.writerow({"user_id": user_id, "conversation_id": conv_id})
                
            except Exception as e:
                logger.error(f"Error fetching conversations for user {user_id}: {e}")
                continue

    # Shuffle the conversations
    logger.info(f"Shuffling {len(all_conversations)} conversations...")
    random.shuffle(all_conversations)

    # Second pass: process conversations in random order
    for conv_data in all_conversations:
        conv_id = conv_data["conversation_id"]
        user_id = conv_data["user_id"]
        
        logger.info(f"Fetching messages for conversation: {conv_id} (User: {user_id})")

        try:
            messages = client.get_conversation_messages(conv_id)
            # Format messages into the desired structure
            formatted_messages = client.format_conversation_messages(messages)
            
            # Prepare the conversation JSON data
            conv_data = {
                "conversation": conv_data["conversation"],
                "messages": messages,
                "formatted_messages": formatted_messages
            }

            # Save conversation JSON to file
            conv_file_path = os.path.join(OUTPUT_DIR, CONVERSATIONS_DIR, f"conversation_{conv_id}.json")
            with open(conv_file_path, 'w') as f:
                json.dump(conv_data, f, indent=4)
            
            logger.info(f"Saved conversation {conv_id} to {conv_file_path}")

        except Exception as e:
            logger.error(f"Error processing conversation {conv_id}: {e}")
            continue

        # Short delay to respect rate limits
        time.sleep(0.5)

    logger.info("Data processing completed. Files saved locally.")

def main():
    process_data()

if __name__ == "__main__":
    main() 