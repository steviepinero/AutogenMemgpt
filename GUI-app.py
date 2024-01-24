import asyncio
import secrets
import autogen

from config import OPENAI_API_KEY
import memgpt.autogen.memgpt_agent as memgpt_autogen
import memgpt.autogen.interface as autogen_interface
import memgpt.presets as presets
from memgpt.persistence_manager import InMemoryStateManager
import openai


import PySimpleGUI as sg
import threading
import queue

openai.api_key = OPENAI_API_KEY # this is the API key for the OpenAI API (https://beta.openai.com/docs/developer-quickstart/your-api-keys)

config_list = [
    {
        'model': 'gpt-3.5-turbo', # GPT-3 model (https://beta.openai.com/docs/api-reference/available-models)
    }
]

USE_MEMGPT = True

import random
import asyncio

llm_config={
    "seed": secrets.SystemRandom().randint(1, 10000), # random seed
    "config_list": config_list, # list of API keys 
}

user_proxy = autogen.UserProxyAgent(
    name="User_proxy",
    system_message="A human admin.",
    code_execution_config={"last_n_messages": 2, "work_dir": "groupchat"},
    human_input_mode="TERMINATE",
    default_auto_reply="You are going to figure all out by your own. You are the expert. "
    "Work by yourself, the user won't reply until you output `TERMINATE` to end the conversation.",
    is_termination_msg=lambda msg: msg == "TERMINATE",
)

interface = autogen_interface.AutoGenInterface() # how MemGPT talks to AutoGen
persistence_manager = InMemoryStateManager()
persona = "I\'m a 10x software engineer at a OpenAI."
human = "I\'m a scrum manager at a FAANG tech company."
memgpt_agent = presets.use_preset(presets.DEFAULT_PRESET, None, 'gpt-4', persona, human, interface, persistence_manager)

# MemGPT coder
coder = memgpt_autogen.MemGPTAgent(
    name="MemGPT_coder",
    agent=memgpt_agent,
    )

cto = memgpt_autogen.MemGPTAgent(
    name="MemGPT_CTO",
    agent=memgpt_agent,
)
# non-MemGPT PM
pm = autogen.AssistantAgent(
    name="Product_manager",
    system_message="Creative in software product ideas.",
    llm_config=llm_config,
)

groupchat = autogen.GroupChat(agents=[user_proxy, coder, cto, pm],
                                      messages=[],
                                      max_round=12)

manager = autogen.GroupChatManager(groupchat=groupchat, 
                                   llm_config=llm_config)


#default request
request = "I need a new feature for the app."

# Create a queue to store the messages
message_queue = queue.Queue()



# Function to run the asyncio event loop
def start_asyncio_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_forever()

# Start the asyncio loop in a separate thread
asyncio_thread = threading.Thread(target=start_asyncio_loop, daemon=True)
asyncio_thread.start()

# Function to handle sending messages
def send_message(message):
    asyncio.run_coroutine_threadsafe(user_proxy.initiate_chat(manager, message=message), asyncio.get_event_loop())
    #add responses to the queue
    message_queue.put(message)


# Function to update the messages in the GUI
def update_messages(window):
    while not message_queue.empty():
        message = message_queue.get()
        window['-TERMINAL-'].update(message + '\n', append=True)

# Create a new PySimpleGUI window
layout = [[sg.Multiline(size=(100, 40), key='-TERMINAL-', autoscroll=True, auto_refresh=True, 
          reroute_stdout=True, reroute_stderr=True, disabled=True)],

          [sg.Input(size=(44, 1), justification='center',  key='-INPUT-'), sg.Button('Send', bind_return_key=True)]]

window = sg.Window('Chat', layout, finalize=True)





# Main function
async def main():
    await user_proxy.initiate_chat(manager, message=request)
    await coder.initiate_chat(manager, message="I can do it.")

# Run the main function using asyncio
def run_main():
    asyncio.run(main())

while True:

    event, values = window.read(timeout=100)  # Add a timeout to allow periodic updates

    try:
        if event == sg.WIN_CLOSED:
            break
        if event == 'Send':
            message = values['-INPUT-']
            window['-INPUT-'].update('')
            message_queue.put(f"User: {message}")
            send_message(message)

        update_messages(window)
    except Exception as e:
        window['-TERMINAL-'].update(f"An error occurred: {e}\n", append=True)
        
window.close()

        





#TODO:
# handle exceptions and display custom error messages
# path_to_save="groupchat", # where to save the conversation history
# path_to_load="groupchat", # where to load the conversation history
# create page to make an agent
# create page for user api key
