import os
import json
import requests
import asyncio
from dotenv import load_dotenv
from openai import OpenAI
from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel, function_tool
from agents import Agent, Runner, set_tracing_disabled
import gradio as gr
from prompts import get_analysts_prompt, get_aggregator_prompt

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


def get_llm_client(llm_provider):
    if llm_provider == 'gemini':
        api_key = google_api_key
        base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
        model_name = "gemini-2.5-flash"

    if llm_provider == 'local':
        api_key = "ollama"
        base_url = "http://localhost:11434/v1"
        model_name = "minimax-m2.5:cloud"

    if llm_provider == 'sarvam':
        api_key = sarvam_api_key
        base_url = "https://api.sarvam.ai/v1"
        model_name = 'sarvam-30b'

    client = OpenAI(api_key=api_key, base_url=base_url)
    async_client = AsyncOpenAI(api_key=api_key,
                               base_url=base_url)

    model = OpenAIChatCompletionsModel(
        model=model_name,
        openai_client=async_client
    )

    return model

available_llms = ['Gemini', 'Ollama', 'Sarvam']

gemini_agent = Agent(
    name="Gemini Researcher Agent",
    instructions=get_analysts_prompt(),
    model=get_llm_client('gemini')
)

ollama_agent = Agent(
    name="Ollama Researcher Agent",
    instructions=get_analysts_prompt(),
    model=get_llm_client('local')
)

sarvam_agent = Agent(
    name="Sarvam Researcher Agent",
    instructions=get_analysts_prompt(),
    model=get_llm_client('sarvam')
)

aggregator_agent = Agent(
    name="Final Aggregator Agent",
    instructions=get_aggregator_prompt(available_llms),
    model=get_llm_client('gemini')
)


## Executors
async def run_worker(agent, message):
    result = await Runner.run(agent, message)

    return {
        "agent": agent.name,
        "analysis": result.final_output
    }

async def task_orchestrators(message):
    tasks = [
        run_worker(gemini_agent, message),
        run_worker(ollama_agent, message),
        run_worker(sarvam_agent, message)
    ]

    results = await asyncio.gather(*tasks)
    cleaned_results = []

    for r in results:
        if isinstance(r, Exception):
            print("Worker failed:", r)
            continue
        if r:
            cleaned_results.append(r)
    return cleaned_results

async def aggregator(results):
    combined = ""
    for r in results:
        combined += f"{r['agent']} Analysis:\n{r['analysis']}\n\n"

    final = await Runner.run(aggregator_agent, combined)
    return final.final_output

async def pipeline(message):

    yield "Starting analysis..."

    results = []

    tasks = {
        "Gemini": run_worker(gemini_agent, message),
        "Ollama": run_worker(ollama_agent, message),
        "Sarvam": run_worker(sarvam_agent, message)
    }

    for model, task in tasks.items():

        try:
            result = await task

            if result:
                results.append(result)
                print(f"--- {model} ---")
                print(result)

            yield f"{model} analysis completed"

        except Exception:
            yield f"{model} skipped due to error"

    yield "Generating final consensus summary..."

    final = await aggregator(results)

    yield final

async def run_pipeline(message):

    results = await task_orchestrators(message)
    for r in results:
        print("\n---", r["agent"], "---")
        print(r["analysis"])
    final = await aggregator(results)
    return final

def chat(message, history):
    yield "Starting analysis..."
    yield "Running Analyst agents..."
    result = asyncio.run(run_pipeline(message))
    yield "Generating final consensus summary..."
    yield result


demo = gr.ChatInterface(chat)
demo.launch()

## --- Test ---
# async def test_workers():
#
#     message = "Explain the impact of AI in finance."
#
#     results = await task_orchestrators(message)
#
#     for r in results:
#         print("\n---", r["agent"], "---")
#         print(r["analysis"])
#
#
# asyncio.run(test_workers())
