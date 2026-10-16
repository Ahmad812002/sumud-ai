import chromadb
import os

_client = None

def get_chroma_client():
    global _client
    # _client = chromadb.PersistentClient(path="C:/Users/96279/OneDrive/Desktop/Ahmad-proj/sumud-ai/data_access/")
    if _client is None:
        _client = chromadb.CloudClient(
            tenant='f4693080-0a9c-4c15-b7b0-8596835296b3',
            database='ahmad_database',
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
        print("Fetching documents from the embeddings collection...")
        print(get_embeddings_collection().get())
        return get_embeddings_collection().get()
    except Exception as e:  
        raise RuntimeError(f"Failed to get documents: {str(e)}")

def get_profile_collection():
    try:
        return get_chroma_client().get_or_create_collection(name="profile")
    except Exception as e:
        raise RuntimeError(f"Failed to get embeddings collection: {str(e)}")
