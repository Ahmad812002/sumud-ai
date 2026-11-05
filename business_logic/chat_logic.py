from config.prompts import chat_prompt
import data_access.embeddings
import business_logic.llm
import json

# This function is to process the chat message, it will take the message as input and chunk it and search for relevant information to generate the response from the LLM.
def process_chat(message):

    embedded_vector = get_embedding(message)
    vector_embedding_result = get_embedding_result(embedded_vector, 8)
            
    if vector_embedding_result is not None:
        chunks = "\n".join([chunk['documents'] for chunk in vector_embedding_result])

    prompt = chat_prompt(chunks, message)
    reply = business_logic.llm.llm_chat(prompt, message)


    if reply is None: 
        return { "ai_answer": "Couldn't generate a response. Please try again." }
    if reply is None and chunks is not None: 
        return { "ai_answer": "I found relevant information but couldn't generate a response. Please try again." }
    
    return { "ai_answer": reply }

# getting embedding of the message to search for relevant information in the vector database.
def get_embedding(message):
    try:
        return data_access.embeddings.get_embedding(message)
    except Exception as e:
        raise ValueError(f"Error occurred while getting embedding: {str(e)}")

# getting embedding result from the vector database to find relevant information for the message.
def get_embedding_result(embedded_vector, n_results):
    try:
        return data_access.embeddings.search_embedding(embedded_vector, n_results)
    except Exception as e:
        raise ValueError(f"Error occurred while searching embedding: {str(e)}")