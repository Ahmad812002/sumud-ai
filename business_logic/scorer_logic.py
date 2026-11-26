from config.prompts import job_scorer_prompt
from clients import llm
from config.settings import DEFAULT_N_RESULTS, THRESHOLD 
import json, exceptions
from business_logic.embeddings_logic import  find_relevant_chunks
from clients.embedding_client import get_embeddings


# It will get the embedding of the entire job description and search for similar documents in the database.
def process_job_description(job_description):
    # for multilingual search_query returns null the main casue is nomic-embed-text-v1.5. 
    query_vector = get_embeddings([job_description], "search_query")
    profile_chunks = find_relevant_chunks(query_vector, DEFAULT_N_RESULTS, THRESHOLD)

    # search_embedding(job_embedding, DEFAULT_N_RESULTS, RELEVANCE_MAX_DISTANCE)
    if profile_chunks:
        return profile_chunks
    return None

def format_scorer_result_json(ai_reply):
    try:
        result = json.loads(ai_reply)
    except json.JSONDecodeError as e:
        raise exceptions.LLMResponseError("The AI response could not be parsed") from e
    return {
        "fit_score": result['fit_score'],
        "fit_category": result['fit_category'],
        "matching_points": result['matching_points'],
        "gaps": result['gaps'],
        "soft_skills": result['soft_skills'],
        "reasoning": result['reasoning']
    }
       
def run_scorer(job_description: str, job_preferences: str):
    # next plan (using the name of the user after adding Authentication and multi-user support)
    # validate

    if len(job_description.strip()) < 50:
        raise exceptions.InvalidInputError("No relevant profile information found. Add documents first.")
        
        # process
    profile_chunks = process_job_description(job_description)
    
    if(profile_chunks is None):
        return None
        
    formatted_prompt = job_scorer_prompt(profile_chunks, job_preferences)
        
    raw_result = llm.llm_scorer(formatted_prompt, job_description)

    # this looks like string but aren't until resolved (lazy object)
    parsed = format_scorer_result_json(raw_result)
    
    return {
        "fit_score": parsed['fit_score'],
        "fit_category": parsed['fit_category'],
        "matching_points": parsed['matching_points'],
        "gaps": parsed['gaps'],
        "soft_skills": parsed['soft_skills'],
        "reasoning": parsed['reasoning'],
        "profile_chunks": profile_chunks
    }