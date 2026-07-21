import requests
import json
import logging
import uuid
import time

logger = logging.getLogger(__name__)

DEFAULT_API_URL = "https://api.deepai.org/hacking_is_a_serious_crime"
DEFAULT_API_KEY = "tryit-29313838055-92efd3f13305fd73765982f1e4bd8c0b"
MAX_RETRIES = 3
RETRY_DELAY = 2
REQUEST_TIMEOUT = 30


class AiError(Exception):
    pass


class Ai:
    def __init__(self, name="eldorado", api_key=None, api_url=None):
        self.name = name
        self.session_uuid = str(uuid.uuid4())
        self.api_key = api_key or DEFAULT_API_KEY
        self.api_url = api_url or DEFAULT_API_URL
        self.history = [{
            "role": "system",
            "content": f"You are {name}, answer to user question with the minimum words and gently"
        }]

    def ask(self, query: str) -> str:
        self.history.append({
            "role": "user",
            "content": query
        })

        history_str = json.dumps(self.history)

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "api-key": self.api_key,
            "Origin": "https://deepai.org",
            "Connection": "keep-alive"
        }
        files = {
            "chat_style": (None, "chat"),
            "chatHistory": (None, history_str),
            "model": (None, "standard"),
            "session_uuid": (None, self.session_uuid),
            "hacker_is_stinky": (None, "very_stinky"),
            "enabled_tools": (None, '["image_generator","image_editor"]')
        }

        last_exception = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    files=files,
                    timeout=REQUEST_TIMEOUT
                )
                response.raise_for_status()

                content = response.text
                if not content:
                    raise AiError(f"Empty response from API for {self.name}")

                logger.info(f"[{self.name}] Got response (attempt {attempt})")
                self.history.append({
                    "role": "assistant",
                    "content": content
                })
                return content

            except requests.exceptions.Timeout:
                last_exception = AiError(f"Request timed out for {self.name}")
                logger.warning(f"[{self.name}] Timeout on attempt {attempt}/{MAX_RETRIES}")

            except requests.exceptions.ConnectionError:
                last_exception = AiError(f"Connection failed for {self.name}")
                logger.warning(f"[{self.name}] Connection error on attempt {attempt}/{MAX_RETRIES}")

            except requests.exceptions.HTTPError as e:
                last_exception = AiError(f"HTTP error for {self.name}: {e}")
                logger.warning(f"[{self.name}] HTTP error on attempt {attempt}/{MAX_RETRIES}: {e}")

            except requests.exceptions.RequestException as e:
                last_exception = AiError(f"Request failed for {self.name}: {e}")
                logger.warning(f"[{self.name}] Request error on attempt {attempt}/{MAX_RETRIES}: {e}")

            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY * attempt)

        raise last_exception
