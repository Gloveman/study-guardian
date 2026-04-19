import os
from dotenv import load_dotenv

load_dotenv()

def load_openai_key():
    OPENAI_API_KEY = os.getenv("OPENAI_KEY")
    os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY