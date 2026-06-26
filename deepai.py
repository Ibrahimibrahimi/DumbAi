import requests
import json


class Ai:
    def __init__(self, name="eldorado"):
        self.name = name
        self.history = [{
            "role": "system",
            "content": f"You are {name} , answer to user question with the minimum words and gently"
        }]
        self.url = "https://api.deepai.org/hacking_is_a_serious_crime"

    def ask(self, query: str):
        # add query to history
        self.history.append({
            "role": "user",
            "content": query
        })

        # dumps history
        history_str = json.dumps(self.history)

        # create headers and files
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "api-key": "tryit-29313838055-92efd3f13305fd73765982f1e4bd8c0b",
            "Origin": "https://deepai.org",
            "Connection": "keep-alive"
        }
        files = {
            "chat_style": (None, "chat"),
            "chatHistory": (None, history_str),
            "model": (None, "standard"),
            "session_uuid": (None, "bb3d57a9-405f-40e9-a6dc-0a831175d7b4"),
            "hacker_is_stinky": (None, "very_stinky"),
            "enabled_tools": (None, '["image_generator","image_editor"]')
        }

        # send post request
        response = requests.post(self.url, headers=headers, files=files)
        self.history.append({
            "role": "assistant",
            "content": response.text
        })
        return response.text
