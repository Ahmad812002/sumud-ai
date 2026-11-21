from nomic import embed
from fastapi import HTTPException
import numpy as np


# This function is to get the embedding of a given text, it will return the embedding vector.
def get_embedding(text):
    try:
        response = embed.text(
            texts=[text],
            model="nomic-embed-text-v1.5",
            task_type="search_document",
        )
        embeddings = np.array(response['embeddings'][0])
        return embeddings
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred while generating embedding: {e}")
    