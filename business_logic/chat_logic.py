import data_access.embeddings
import json


def get_embedding(message):
    try:
        return data_access.embeddings.get_embedding(message)
    except Exception as e:
        raise ValueError(f"Error occurred while getting embedding: {str(e)}")


def get_embedding_result(embedded_vector, n_results):
    try:
        response = data_access.embeddings.search_embedding(embedded_vector, n_results)

        print(response)
        # return format_chat_response_json(response)
    except Exception as e:
        raise ValueError(f"Error occurred while searching embedding: {str(e)}")

def format_chat_response_json(response):
    response = json.loads(response)
    if response is not None:
        return response
    return ""