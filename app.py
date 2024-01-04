import asyncio
import autogen

from config import OPENAI_API_KEY
import memgpt.autogen.memgpt_agent as memgpt_autogen
import memgpt.autogen.interface as autogen_interface
import memgpt.presets as presets
from memgpt.persistence_manager import InMemoryStateManager
import openai
import secrets



openai.api_key = OPENAI_API_KEY # This is where you'd place the API key for the OpenAI API

config_list = [
    {
        'model': 'gpt-4', # GPT-4 model
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
    human_input_mode="TERMINATE ",
    default_auto_reply="You are going to figure all out by your own. "
    "Work by yourself, the user won't reply until you output `TERMINATE` to end the conversation.",
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

groupchat = autogen.GroupChat(agents=[user_proxy, coder, cto, pm], messages=[], max_round=12)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

request = "We need a simple application that will reset a users IP settings to DHCP. The application needs to be a simple button that gives feedback when pressed and should be installed as an exe"

async def main():
    await user_proxy.initiate_chat(manager, message=request)
    await coder.initiate_chat(manager, message="I can do it.")

# Run the main function using asyncio
asyncio.run(main())

