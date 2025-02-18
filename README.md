# Freshchat Conversation Exporter

This tool exports conversations from Freshchat, including user data, conversation details, and messages. It saves all data locally in structured CSV and JSON files.

## Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create and activate a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

### Environment Variables Setup

1. Copy the sample environment file to create your own `.env` file:
```bash
cp .env.sample .env
```

2. Edit the `.env` file and add your Freshchat credentials:
```
FRESHCHAT_ACCOUNT_URL=your-account.freshchat.com
FRESHCHAT_API_KEY=your-api-key
```

Note: You can find your API key in the Freshchat dashboard under Settings > API Tokens.

## Running the Exporter

1. Make sure your virtual environment is activated:
```bash
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

2. Run the script:
```bash
python main.py
```

The script will:
1. Fetch all users from your Freshchat account
2. Retrieve all conversations for each user
3. Download all messages from each conversation
4. Save everything locally in the `output` directory

## Output Files

The script creates an `output` directory with the following structure:

```
output/
├── users.csv                  # List of all users with their IDs
├── conversation_ids.csv       # Mapping between user IDs and conversation IDs
└── conversations/            # Directory containing all conversation data
    ├── conversation_123.json
    ├── conversation_456.json
    └── ...
```

### File Contents

1. `users.csv`:
   - Contains user IDs for all users in your Freshchat account
   - Format: `user_id`

2. `conversation_ids.csv`:
   - Maps user IDs to their conversation IDs
   - Format: `user_id,conversation_id`

3. `conversations/*.json`:
   - One JSON file per conversation
   - Contains:
     - Conversation metadata
     - All messages in the conversation
     - Formatted messages with role labels (User/Agent)
   - Format:
     ```json
     {
       "conversation": {/* conversation metadata */},
       "messages": [/* raw message objects */],
       "formatted_messages": [
         {
           "role": "User/Agent",
           "content": "message text"
         }
       ]
     }
     ```

## Progress and Logging

- The script logs its progress to the console
- You can see:
  - Number of users being processed
  - Current conversation being downloaded
  - Any errors that occur during the process

## Rate Limiting

The script includes automatic rate limit handling:
- Respects Freshchat's API rate limits
- Implements exponential backoff when limits are hit
- Includes a 0.5-second delay between requests

## Error Handling

- Failed requests are automatically retried
- If a conversation fails to download, the script continues with the next one
- All errors are logged to the console
