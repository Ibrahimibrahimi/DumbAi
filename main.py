from deepai import Ai
from colorama import Fore, Style
import json

deep1 = Ai("eldorado1")
deep2 = Ai("eldorado2")

deep1_answer, deep2_answer = "", f"Hi im {deep2.name}, how can i assist you"


history_chat = []
with open("history_of_two_bots.json", "w") as file:
    json.dump(history_chat, file)

i = 0
while True:
    i += 2
    deep1_answer = deep1.ask(deep2_answer)
    print(f"{Fore.GREEN}Deep 1 [{i}] : {Style.RESET_ALL}", deep1_answer)
    
    # add for deep1
    history_chat.append({
        "model": "deep1",
        "text": deep1_answer
    })

    deep2_answer = deep2.ask(deep1_answer)
    print(f"{Fore.RED}Deep 2 [{i}]: {Style.RESET_ALL}", deep2_answer)
    
    history_chat.append({
        "model": "deep2",
        "text": deep2_answer
    })
    if i == 500:
        break
with open("history_of_two_bots.json", "w") as file:
    json.dump(history_chat, file)
