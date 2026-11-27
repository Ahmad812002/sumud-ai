
from dotenv import load_dotenv
from openai import OpenAI
import os
import nomic
from exceptions import ExternalServiceError

load_dotenv()

def initialize_client():
    try:
        client = OpenAI(
            # This is the API key which is inside .env file.
            api_key=os.environ.get("GEMINI_API_KEY"),
            base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
        )
    except Exception as e:
        raise ExternalServiceError("Somthing went wrong! can't connect to open_ai") from e


    # Initialize and log into the Nomic Atlas client using the API key.
    nomic.login(token=os.environ.get("NOMIC_API_KEY"))

    return client