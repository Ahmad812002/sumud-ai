import chromadb
import os

_client = None

def get_chroma_client():
    global _client
    if _client is None:
        if(os.get_env('CHROMA_TENANT') is None or os.getenv('CHROMA_DATABASE') is None or os.getenv('CHROMA_API_KEY') is None):
                print("ChromaDB environment variables are not set. Please set CHROMA_TENANT, CHROMA_DATABASE, and CHROMA_API_KEY in the .env file.")
                raise RuntimeError("ChromaDB environment variables are not set. Please set CHROMA_TENANT, CHROMA_DATABASE, and CHROMA_API_KEY in the .env file.")   
        _client = chromadb.CloudClient(
            tenant=os.getenv('CHROMA_TENANT'),
            database=os.getenv('CHROMA_DATABASE'),
            api_key=os.getenv('CHROMA_API_KEY')
        )
    return _client


def get_preferences_collection():
    try:
        return get_chroma_client().get_or_create_collection(name="preferences")
    except Exception as e:
        raise RuntimeError(f"Failed to get preferences collection: {str(e)}")   


def get_embeddings_collection():
    try:
        return get_chroma_client().get_or_create_collection(name="embeddings")
    except Exception as e:
        raise RuntimeError(f"Failed to get embeddings collection: {str(e)}")

def get_records():
    try:
        return get_embeddings_collection().get()
    except Exception as e:  
        raise RuntimeError(f"Failed to get documents: {str(e)}")

