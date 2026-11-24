from nomic import embed
import numpy as np
from exceptions import EmbeddingServiceError


# This function is to get the embedding of a given text, it will return the embedding vector.
def get_embeddings(chunks, task_type="search_document"):
    try:
        # i think we need to use another version or model
        response = embed.text(
            texts=chunks,
            model="nomic-embed-text-v1.5",
            task_type=task_type,
        )
        return np.array(response['embeddings']).tolist()
    except Exception as e:
        raise EmbeddingServiceError("Error occurred while generating embedding") from e
    