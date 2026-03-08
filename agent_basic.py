from ollama import chat
from ollama import ChatResponse
from ollama import Client

client = Client()

messages = [
  {
    'role': 'user',
    'content': 'What is Transformer model',
  },
]

for part in client.chat('minimax-m2.5:cloud', messages=messages, stream=True):
  print(part.message.content, end='', flush=True)