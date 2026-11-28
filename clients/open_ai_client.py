from dotenv import load_dotenv
from openai import OpenAI
import os
import nomic
from exceptions import ExternalServiceError, InvalidInputError
from functools import lru_cache

@lru_cache(maxsize=1)
def initialize_client():
    load_dotenv()
    try:
        gemini_key = os.environ.get("GEMINI_API_KEY")
        nomic_key = os.environ.get("NOMIC_API_KEY")
        print("nomic: ", nomic_key)
        print("gemini",gemini_key)

        if not gemini_key or not nomic_key:
            raise InvalidInputError("Missing GEMINI_API_KEY or NOMIC_API_KEY in .env")
        client = OpenAI(
            # This is the API key which is inside .env file.
            api_key=gemini_key,
            base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
        )
            # Initialize and log into the Nomic Atlas client using the API key.
        nomic.login(token=nomic_key)
    except Exception as e:
        raise ExternalServiceError("Somthing went wrong! can't connect to open_ai") from e

    return client