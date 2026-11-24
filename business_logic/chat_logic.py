from config.prompts import chat_prompt
from clients.embedding_client import get_embeddings
from config.settings import CHAT_THRESHOLD
from business_logic.embeddings_logic import find_relevant_chunks
from data_access.embeddings import search_embedding
from llm import llm_chat

# This function is to process the chat message, it will take the message as input and chunk it and search for relevant information to generate the response from the LLM.
def process_chat(message):

    # getting embedding of the message to search for relevant information in the vector database.
    embedded_chat_vector = get_embeddings([message])
    relative_chat_chunks = find_relevant_chunks(embedded_chat_vector, 8, CHAT_THRESHOLD)
            
    prompt = chat_prompt(relative_chat_chunks, message)
    reply = llm_chat(prompt, message)
    
    return { "ai_answer": reply }
    