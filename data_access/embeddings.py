from dotenv import load_dotenv
from data_access.db import get_embeddings_collection
from exceptions import VectorStoreError


load_dotenv()

# This function is to store the embedding in ChromaDB, it will take the document id, text and embedding vector as input and store it in the collection.
def store_embeddings(_ids, _documents, _embeddings, _source, _fingerprint, _type):
    
    try:
        get_embeddings_collection().add(
            ids = _ids,
            documents = _documents,
            embeddings = _embeddings,
            metadatas = [{ "source": _source, "fingerprint": _fingerprint, "type": _type } for _ in _ids]    
        )
        return True
    except Exception as e:
        raise VectorStoreError("Could not store the document chunks") from e
# This function is to search the embedding in ChromaDB, it will take the query vector as input and return the top 3 closest documents.
def search_embedding(query_vector, n_results):
    try:
        results = get_embeddings_collection().query(
            query_embeddings=query_vector,
            n_results=n_results,
        )
    except Exception as e:
        raise VectorStoreError("Error occurred while searching embedding") from e

    return [
        {"distance": d, "document": doc, "metadata": m}
        for d, doc, m in zip(
            results["distances"][0],
            results["documents"][0],
            results["metadatas"][0],
        )
    ]
def is_document_exists(fingerprint):
    result = get_embeddings_collection().get(
        where={"fingerprint": fingerprint},
        limit=1,
        include=[]  # Optional: skips fetching metadata/documents to make the query faster
    )
    return len(result["ids"]) > 0