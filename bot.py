import openai
from dotenv import load_dotenv
import os
import json

import gpt_functions, utils

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

def parse_function_reponse(message):
    function_call = message["function_call"]
    function_name = function_call["name"]

    print("shopGPT: Fetching products for you....")

    try:
        arguments = json.loads(function_call["arguments"])
        if hasattr(gpt_functions, function_name):
            function_response = getattr(gpt_functions, function_name)(**arguments)
        else:
            function_response = "ERROR: Called unknown function"
    except:
        function_response = "ERROR: Invalid arguments"

    return (function_name, function_response)


def run_conversation(message, chat_history=[]):
    chat_history.append(message) # add message to message history

    # log the chat for later reference
    with open("logs.json", "w") as f:
        f.write(json.dumps(messages, indent=4))

    response = openai.ChatCompletion.create(
        messages=chat_history,
        model="gpt-3.5-turbo-0613",
        functions=gpt_functions.definitions,
        function_call="auto",
    )

    # reply from the chatgpt
    reply = response["choices"][0]["message"]
    chat_history.append(reply)

    # if chatgpt wants to do a function call
    if 'function_call' in reply:
        function_name, function_response = parse_function_reponse(reply)
        message = {
            "role": "function",
            "name": function_name,
            "content": function_response
        }        
    else:
        user_message = input("\nShopGPT: " + reply["content"] + "\n\nYou: ")
        message = {
            "role": "user",
            "content": user_message
        }

    run_conversation(message=message, chat_history=chat_history)




chat_history = [{
    "role": "system",
    "content": utils.ROLE_PROMPT,
}]

user_message = input("shopGPT: Hi, How can I help you?\n\nYou: ")
message = {
    "role": "user",
    "content": user_message
}
run_conversation(message=message, chat_history=chat_history)