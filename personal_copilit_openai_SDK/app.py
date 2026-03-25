import os
import json
import requests
from dotenv import load_dotenv
from openai import OpenAI
from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel, function_tool
from agents import Agent, Runner, set_tracing_disabled
import gradio as gr

from prompt import get_agent_instruction

load_dotenv(override=True)

openai_api_key = os.getenv('OPENAI_API_KEY')
claude_api_key = os.getenv('CLAUDE_API_KEY')
google_api_key = os.getenv('GEMINI_API_KEY')
deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
groq_api_key = os.getenv('GROQ_API_KEY')
sarvam_api_key = os.getenv('SARVAMAI_API_KEY')
mistral_api_key = os.getenv('MISTRAL_API_KEY')

pushover_user_key = os.getenv("PUSHOVER_USER_KEY")
pushover_api_key = os.getenv("PUSHOVER_API_TOKEN")
pushover_base_url = "https://api.pushover.net/1/messages.json"

llm_provider = "gemini"

if llm_provider == 'gemini':
    client = OpenAI(api_key=google_api_key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
    async_client = AsyncOpenAI(api_key=google_api_key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
    model_name = "gemini-2.5-flash"

if llm_provider == 'local':
    client = OpenAI(api_key="ollama", base_url="http://localhost:11434/v1")
    async_client = AsyncOpenAI(api_key="ollama", base_url="http://localhost:11434/v1")
    model_name = "minimax-m2.5:cloud"

if llm_provider == 'sarvam':
    client = OpenAI(api_key=sarvam_api_key, base_url="https://api.sarvam.ai/v1")
    async_client = AsyncOpenAI(api_key=sarvam_api_key, base_url="https://api.sarvam.ai/v1")
    model_name = 'sarvam-30b'

if llm_provider == 'claude':
    client = OpenAI(api_key=claude_api_key, base_url="https://api.anthropic.com/v1/")
    async_client = AsyncOpenAI(api_key=claude_api_key, base_url="https://api.anthropic.com/v1/")
    model_name = 'claude-haiku-4-5-20251001'

if llm_provider == 'mistral':
    client = OpenAI(api_key=mistral_api_key, base_url="https://api.mistral.ai/v1/")
    async_client = AsyncOpenAI(api_key=mistral_api_key, base_url="https://api.mistral.ai/v1/")
    model_name = "mistral-small-2503"


def push(message):
    print(f"Push: {message}")
    payload = {"user": pushover_user_key, "token": pushover_api_key, "message": message}
    requests.post(pushover_base_url, data=payload)


@function_tool
def lookup_profile():
    """
    Lookup Owner's Professional profile and other details
    """
    with open ('profile.txt') as f:
        return f.read()


@function_tool
def store_user_details(email, name="Name not provided", notes="not provided"):
    """
    Use this tool to record that a user is interested in being in touch and provided an email address
    :param email: The email address of this user
    :param name: The user's name, if they provided it
    :param notes: Any additional information about the conversation that's worth recording to give context
    """
    push(f"Received interest from {name} with email {email} and notes {notes}")
    return {"recorded": "ok"}


@function_tool
def store_unknown_question(question):
    """
    Always use this tool to record any question that couldn't be answered as you didn't know the answer
    :param question: The question that couldn't be answered
    """
    push(f"Recording {question} asked that I couldn't answer")
    return {"recorded": "ok"}


model = OpenAIChatCompletionsModel(
    model=model_name,
    openai_client=async_client
)

set_tracing_disabled(disabled=True)

owner = "Pratik"
instructions = get_agent_instruction(owner)
tools = [lookup_profile, store_user_details, store_unknown_question]
agent = Agent(
    name="Personal Brand Agent",
    instructions=instructions,
    model=model,
    tools=tools,
)


def chat(message, history):
    result = Runner.run_sync(agent, message)
    # op = result.final_output()
    return result.final_output

# print(chat("who are you?"))
#


def launch_ui():
    interface = gr.ChatInterface(chat)
    interface.launch(share=True)


launch_ui()