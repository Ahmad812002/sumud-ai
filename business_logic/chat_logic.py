


import data_access.embeddings


def get_embedding(message):
    try:
        print("get embedding: ",data_access.embeddings.get_embedding(message))
        return data_access.embeddings.get_embedding(message)
    except Exception as e:
        raise ValueError(f"Error occurred while getting embedding: {str(e)}")


def get_embedding_result(embedded_vector):
    try:
        print("embedding result: ",data_access.embeddings.search_embedding(embedded_vector))
        return data_access.embeddings.search_embedding(embedded_vector)
    except Exception as e:
        raise ValueError(f"Error occurred while searching embedding: {str(e)}")