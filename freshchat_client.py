import requests
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FreshchatClient:
    def __init__(self, account_url, api_key, max_retries=3, backoff_factor=1):
        """
        Initializes FreshchatClient.
        :param account_url: e.g. "youraccount.freshchat.com"
        :param api_key: Provided Freshchat API key.
        :param max_retries: Maximum retry attempts on rate limit or server errors.
        :param backoff_factor: Backoff multiplier for retry delay.
        """
        # If the account_url already starts with http:// or https://, use it as is (after stripping any trailing slashes)
        if account_url.startswith('http://') or account_url.startswith('https://'):
            self.base_url = f"{account_url.rstrip('/')}/v2"
        else:
            self.base_url = f"https://{account_url}/v2"
        self.api_key = api_key
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.headers = {
            "Authorization": f"Bearer eyJraWQiOiJjdXN0b20tb2F1dGgta2V5aWQiLCJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJmcmVzaGNoYXQiLCJhdWQiOiJmcmVzaGNoYXQiLCJpYXQiOjE3Mzk3Njc4OTMsInNjb3BlIjoiYWdlbnQ6cmVhZCBhZ2VudDpjcmVhdGUgYWdlbnQ6dXBkYXRlIGFnZW50OmRlbGV0ZSBjb252ZXJzYXRpb246Y3JlYXRlIGNvbnZlcnNhdGlvbjpyZWFkIGNvbnZlcnNhdGlvbjp1cGRhdGUgbWVzc2FnZTpjcmVhdGUgbWVzc2FnZTpnZXQgYmlsbGluZzp1cGRhdGUgcmVwb3J0czpmZXRjaCByZXBvcnRzOmV4dHJhY3QgcmVwb3J0czpyZWFkIHJlcG9ydHM6ZXh0cmFjdDpyZWFkIGFjY291bnQ6cmVhZCBkYXNoYm9hcmQ6cmVhZCB1c2VyOnJlYWQgdXNlcjpjcmVhdGUgdXNlcjp1cGRhdGUgdXNlcjpkZWxldGUgb3V0Ym91bmRtZXNzYWdlOnNlbmQgb3V0Ym91bmRtZXNzYWdlOmdldCBtZXNzYWdpbmctY2hhbm5lbHM6bWVzc2FnZTpzZW5kIG1lc3NhZ2luZy1jaGFubmVsczptZXNzYWdlOmdldCBtZXNzYWdpbmctY2hhbm5lbHM6dGVtcGxhdGU6Y3JlYXRlIG1lc3NhZ2luZy1jaGFubmVsczp0ZW1wbGF0ZTpnZXQgZmlsdGVyaW5ib3g6cmVhZCBmaWx0ZXJpbmJveDpjb3VudDpyZWFkIHJvbGU6cmVhZCBpbWFnZTp1cGxvYWQiLCJ0eXAiOiJCZWFyZXIiLCJjbGllbnRJZCI6ImZjLTZiOGU4MDA5LTZkZmEtNDhiMy1hYjUzLTEwYjJkNDA3MTkxNyIsInN1YiI6ImIxOTE0ODAzLWVlYWMtNDFjNC1hY2FkLTQ4NDczNzA0NDMxNyIsImp0aSI6ImNkNWU1ZTEzLWU2MzktNDMyZC05MDYzLWY4NzcwNTEyODczNyIsImV4cCI6MjA1NTMwMDY5M30.Xa89gQTtSNuKjdy3VJ-pMs5GlJ_X1dxfVALuvT6lBTg",
            "accept": "application/json",
            "Content-Type": "application/json"
        }
        
    def _make_request(self, method, endpoint, params=None, json_data=None):
        """
        Makes an HTTP request and handles retries for rate-limited responses.
        """
        url = f"{self.base_url}{endpoint}"
        retries = 0
        while retries < self.max_retries:
            response = requests.request(method, url, headers=self.headers, params=params, json=json_data)
            if response.status_code == 429:
                # Rate limit exceeded, check for Retry-After header and wait.
                retry_after = int(response.headers.get("Retry-After", 1))
                wait_time = self.backoff_factor * (retry_after or 1)
                logger.warning(f"Rate limit hit. Retrying after {wait_time} seconds...")
                time.sleep(wait_time)
                retries += 1
            elif response.status_code >= 500:
                # Server error, wait a bit and retry.
                logger.warning(f"Server error {response.status_code}. Retrying after {self.backoff_factor} seconds...")
                time.sleep(self.backoff_factor)
                retries += 1
            else:
                break

        if not response.ok:
            logger.error(f"Request failed: {response.status_code} {response.text}")
            response.raise_for_status()

        return response.json()

    def fetch_all_users(self, items_per_page=100):
        """
        Fetches all users using the paginated GET /users endpoint.
        """
        users = []
        page = 1

        while True:
            params = {
                "page": page,
                "items_per_page": items_per_page,
                "created_from": "2020-02-14T00:00:00.000Z"
            }
            logger.info(f"Fetching users, page {page}")
            data = self._make_request("GET", "/users", params=params)

            current_users = data.get("users", [])
            users.extend(current_users)

            pagination = data.get("pagination", {})
            total_pages = pagination.get("total_pages", page)

            if page >= total_pages:
                break
            page += 1

        return users

    def get_user_conversations(self, user_id):
        """
        Fetches all conversations associated with a given user.
        :param user_id: The Freshchat user ID.
        :return: List of conversation objects.
        """
        endpoint = f"/users/{user_id}/conversations"
        logger.info(f"Fetching conversations for user {user_id}")
        data = self._make_request("GET", endpoint)
        return data.get("conversations", [])

    def get_conversation_messages(self, conversation_id):
        """
        Fetches all messages for a given conversation with pagination.
        :param conversation_id: The Freshchat conversation ID.
        :param items_per_page: Maximum messages per page (default 50).
        :return: List of message objects.
        """
        messages = []
        page = 1
        items_per_page = 50  # maximum items per page available for messages

        while True:
            params = {
                "page": page,
                "items_per_page": items_per_page
            }
            endpoint = f"/conversations/{conversation_id}/messages"
            logger.info(f"Fetching messages for conversation {conversation_id}, page {page}")
            data = self._make_request("GET", endpoint, params=params)
            current_messages = data.get("messages", [])
            messages.extend(current_messages)

            # If we get fewer messages than requested, we assume there are no more pages.
            if len(current_messages) < items_per_page:
                break
            page += 1

        return messages

    def format_conversation_messages(self, messages):
        """
        Formats conversation messages into a list of role-content pairs.
        
        :param messages: List of message objects from the conversation
        :return: List of dictionaries with 'role' and 'content' keys
        """
        formatted_messages = []
        
        # Process messages in reverse order to maintain chronological order
        for message in reversed(messages):
            # Skip system messages
            if message.get('message_type') == 'system':
                continue
                
            actor_type = message.get('actor_type', '').lower()
            
            # Map actor types to roles
            role = {
                'user': 'User',
                'agent': 'Agent'
            }.get(actor_type, 'Unknown')
            
            # Extract content from message_parts
            content = ''
            message_parts = message.get('message_parts', [])
            for part in message_parts:
                if 'text' in part and 'content' in part['text']:
                    content = part['text']['content']
                    break
            
            if content:  # Only add messages with content
                formatted_messages.append({
                    'role': role,
                    'content': content
                })
        
        return formatted_messages 