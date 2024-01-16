import asyncio
import autogen
import tkinter as tk
from tkinter import messagebox

from config import OPENAI_API_KEY
import memgpt.autogen.memgpt_agent as memgpt_autogen
import memgpt.autogen.interface as autogen_interface
import memgpt.presets as presets
from memgpt.persistence_manager import InMemoryStateManager
import openai
import secrets

#TODO: Add a section for the user to input their OpenAI API key
openai.api_key = OPENAI_API_KEY

config_list = [
    {
        'model': 'gpt-3.5-turbo',
    }
]

USE_MEMGPT = True

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
)

interface = autogen_interface.AutoGenInterface()
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

#TODO Add a section for the user to input the agents they want to use
#TODO Add a section for the groupchat to be created and view the agents' responses to the request

groupchat = autogen.GroupChat(agents=[user_proxy, coder, cto, pm], messages=[], max_round=12)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

#TODO Add a section for the user to input the request
request = "We need a simple application that will reset a users IP settings to DHCP. The application needs to be a simple button that gives feedback when pressed and should be installed as an exe"


#TODO draft for Ui to create agents. Roughly based on the code in app.py
def create_agent():
    name = name_entry.get()
    persona = persona_entry.get()
    human = human_entry.get()

    if not name or not persona or not human:
        messagebox.showerror("Error", "All fields must be filled out")
        return

    memgpt_agent = presets.use_preset(presets.DEFAULT_PRESET, None, 'gpt-4', persona, human, interface, persistence_manager)
    agent = memgpt_autogen.MemGPTAgent(name=name, agent=memgpt_agent)

    messagebox.showinfo("Success", f"Agent {name} created successfully")

root = tk.Tk()

name_label = tk.Label(root, text="Agent Name")
name_label.pack()
name_entry = tk.Entry(root)
name_entry.pack()

persona_label = tk.Label(root, text="Agent Persona")
persona_label.pack()
persona_entry = tk.Entry(root)
persona_entry.pack()

human_label = tk.Label(root, text="Human Description")
human_label.pack()
human_entry = tk.Entry(root)
human_entry.pack()

create_button = tk.Button(root, text="Create Agent", command=create_agent)
create_button.pack()

root.mainloop()

async def main():
    await user_proxy.initiate_chat(manager, message=request)
    await coder.initiate_chat(manager, message="I can do it.")

asyncio.run(main())



