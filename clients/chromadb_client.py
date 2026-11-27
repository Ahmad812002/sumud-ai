import os
from dotenv import load_dotenv
from exceptions import ExternalServiceError, InvalidInputError
import chromadb
from functools import lru_cache

load_dotenv()

@lru_cache(maxsize=1)
def get_chroma():
    if(os.getenv('CHROMA_TENANT') is None or os.getenv('CHROMA_DATABASE') is None or os.getenv('CHROMA_API_KEY') is None):
        raise InvalidInputError("ChromaDB environment variables are not set. Please set CHROMA_TENANT, CHROMA_DATABASE, and CHROMA_API_KEY in the .env file.")   
    try:    
        return chromadb.CloudClient(
            tenant=os.getenv('CHROMA_TENANT'),
            database=os.getenv('CHROMA_DATABASE'),
            api_key=os.getenv('CHROMA_API_KEY')
        )
    except Exception as e:
        raise ExternalServiceError("Somthing went wrong! can't connect to chromadb") from e