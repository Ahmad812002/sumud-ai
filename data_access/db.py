import chromadb
import os

_client = None

def get_chroma_client():
    global _client
    if _client is None:
        if(os.getenv('CHROMA_TENANT') is None or os.getenv('CHROMA_DATABASE') is None or os.getenv('CHROMA_API_KEY') is None):
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
        raise RuntimeError("Couldn't get embeddings collection") from e

def get_records():
    try:
        collection = get_embeddings_collection().get()
        if(collection is None or 'ids' not in collection or len(collection['ids']) == 0):
            return None
        return collection
    except Exception as e: 
        raise RuntimeError(f"Failed to get documents") from e

# Remove every chunk that belongs to one file.
def delete_chunks_by_fingerprint(fingerprint):
    get_embeddings_collection().delete(where={"fingerprint": fingerprint})

# Remove chunks of every CV except the one just stored.
def delete_old_cv_chunks(keep_fingerprint):
    get_embeddings_collection().delete(
        where={"$and": [{"type": "cv"}, {"fingerprint": {"$ne": keep_fingerprint}}]}
    )