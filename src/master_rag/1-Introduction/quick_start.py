from dotenv import load_dotenv
from openai import OpenAI
from colorama import Fore
import warnings


warnings.filterwarnings("ignore")

# LOAD ENV VARIABLES
load_dotenv()

# Load the model
client = OpenAI(base_url="http://localhost:11434/v1", api_key="olama",)

if __name__ == "__main__":
  # Define a request
  print(Fore.GREEN + "Requesting the model to generate a response..." + Fore.RESET + "\n")

  completion = client.chat.completions.create(
    model="qwen2.5:7b",
    messages=[
      {
        "role": "system",
        "content": "You are a funny assistant, skilled in telling 2-sentence jokes about the topic given"},
      {
        "role": "user",
        "content":"Tell me a joke about the topic 'Python'"}
    ]
  )

  print(Fore.BLUE + completion.choices[0].message.content)

