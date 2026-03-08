import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)

openai_api_key = os.getenv('OPENAI_API_KEY')
anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
google_api_key = os.getenv('GEMINI_API_KEY')
deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
groq_api_key = os.getenv('GROQ_API_KEY')

# Deepseek
"""
deepseek = OpenAI(api_key=deepseek_api_key, base_url="https://api.deepseek.com/v1")
model_name = "deepseek-chat"
"""

# Grok
"""
grok = OpenAI(api_key=groq_api_key, base_url="https://api.groq.com/openai/v1")
model_name = "openai/gpt-oss-120b"
"""

gemini = OpenAI(api_key=google_api_key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
model_name = "gemini-2.5-flash"

prompt = """
Solve this problem step-by-step: 
John has 5 apples, he eats 2. How many apples does he have left? 
Step 1: John starts with 5 apples. 
Step 2: He eats 2 apples, so we need to subtract 2 from 5. 
Step 3: 5 - 2 = 3. 
Answer: John has 3 apples left.

Problem:
Krishna has 10 bananas, he eats 5. How many have left?
"""

messages = [{"role": "user", "content": prompt}]
response = gemini.chat.completions.create(model=model_name, messages=messages)
answer = response.choices[0].message.content

print(answer)