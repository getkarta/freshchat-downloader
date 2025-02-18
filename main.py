import os
import csv
import json
import logging
import time
from config import FRESHCHAT_ACCOUNT_URL, FRESHCHAT_API_KEY, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
from freshchat_client import FreshchatClient
import boto3
import io
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define output directories and CSV file paths.
OUTPUT_DIR = "conversations"
USERS_CSV = "users.csv"
CONV_CSV = "user_conversations.csv"
MSG_CSV = "conversation_messages.csv"

S3_BUCKET = "fc-history"

def process_data():
    # Derive company domain from the FRESHCHAT_ACCOUNT_URL.
    parsed_url = urlparse(FRESHCHAT_ACCOUNT_URL)
    domain = parsed_url.netloc if parsed_url.netloc else FRESHCHAT_ACCOUNT_URL
    if domain.endswith(".freshchat.com"):
         company_domain = domain.replace(".freshchat.com", "")
    else:
         company_domain = domain

    # Initialize boto3 S3 client.
    s3_client = boto3.client("s3", region_name="us-east-1", aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    # Set up in-memory buffers for CSV files.
    users_csv = io.StringIO()
    conv_csv = io.StringIO()

    import csv
    users_writer = csv.DictWriter(users_csv, fieldnames=["user_id"])
    conv_writer = csv.DictWriter(conv_csv, fieldnames=["user_id", "conversation_id"])
    users_writer.writeheader()
    conv_writer.writeheader()

    # Initialize Freshchat API client and fetch all users.
    client = FreshchatClient(FRESHCHAT_ACCOUNT_URL, FRESHCHAT_API_KEY)
    logger.info("Fetching all users...")
    users = client.fetch_all_users()
    logger.info(f"Total users fetched: {len(users)}")

    # Process each user.
    for user in users:
        user_id = user.get("id")
        if not user_id:
            logger.warning("User without id found, skipping.")
            continue

        # Record user id in the CSV buffer.
        users_writer.writerow({"user_id": user_id})
        logger.info(f"Processing user: {user_id}")

        try:
            conversations = client.get_user_conversations(user_id)
            logger.info(f"User {user_id} has {len(conversations)} conversation(s)")
        except Exception as e:
            logger.error(f"Error fetching conversations for user {user_id}: {e}")
            continue

        # Process each conversation.
        for conv in conversations:
            conv_id = conv.get("id") or conv.get("conversation_id")
            if not conv_id:
                logger.warning(f"Conversation with missing id for user {user_id}")
                continue

            # Record mapping of user_id and conversation_id.
            conv_writer.writerow({"user_id": user_id, "conversation_id": conv_id})
            logger.info(f"Fetching messages for conversation: {conv_id}")

            try:
                messages = client.get_conversation_messages(conv_id)
                # Format messages into the desired structure
                formatted_messages = client.format_conversation_messages(messages)
                
                # Prepare the conversation JSON data with both raw and formatted messages
                conv_data = {
                    "conversation": conv, 
                    "messages": messages,
                    "formatted_messages": formatted_messages
                }
                conv_json = json.dumps(conv_data, indent=4)

            except Exception as e:
                logger.error(f"Error fetching messages for conversation {conv_id}: {e}")
                continue

            # Define S3 key: store conversation JSON inside the 'conversations' folder.
            s3_key = f"{company_domain}/conversations/conversation_{conv_id}.json"
            logger.info(f"Uploading conversation {conv_id} JSON to s3://{S3_BUCKET}/{s3_key}")
            s3_client.put_object(Bucket=S3_BUCKET, Key=s3_key, Body=conv_json)

            # Short delay to respect rate limits.
            time.sleep(0.5)

    # Define S3 keys for the CSV files.
    users_csv_key = f"{company_domain}/user.csv"
    conv_csv_key = f"{company_domain}/conversation_ids.csv"

    logger.info(f"Uploading users CSV to s3://{S3_BUCKET}/{users_csv_key}")
    s3_client.put_object(Bucket=S3_BUCKET, Key=users_csv_key, Body=users_csv.getvalue())
    logger.info(f"Uploading conversation IDs CSV to s3://{S3_BUCKET}/{conv_csv_key}")
    s3_client.put_object(Bucket=S3_BUCKET, Key=conv_csv_key, Body=conv_csv.getvalue())

    logger.info("Data processing completed and uploaded to S3.")

def main():
    process_data()

if __name__ == "__main__":
    main() 