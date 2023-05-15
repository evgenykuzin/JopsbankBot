import os
from dotenv import load_dotenv

load_dotenv()


def get_token():
    return os.getenv('BOT_TOKEN')