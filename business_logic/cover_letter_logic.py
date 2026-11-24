import json
from config.prompts import cover_letter_prompt, german_cover_letter_prompt
from clients.llm import llm_cover_letter
import exceptions, re

GERMAN_WORDS = {"die", "der", "das", "und", "für", "sie", "wir", "mit",
                "von", "auf", "suchen", "stelle", "kenntnisse", "erfahrung"}


def run_cover_letter(profile_chunks, job_description, fit_category, matching_points=None, soft_skills=None, reasoning=""):
    language = detect_language(job_description)

    build_prompt = german_cover_letter_prompt if language == "German" else cover_letter_prompt
    prompt = build_prompt(profile_chunks,
        fit_category,
        matching_points or [],     # None -> fresh empty list for this call
        soft_skills or [],
        reasoning,
    )

    cover_letter_response = llm_cover_letter(prompt, job_description)
    return format_cover_letter_json(cover_letter_response)


def detect_language(text: str) -> str:
    words = set(re.findall(r"\w+", text.lower())) 
    # `&` keeps only the words found in both sets
    return "German" if len(words & GERMAN_WORDS) >= 3 else "English"
# Fromating ai json response to be more readable 
def format_cover_letter_json(ai_reply):
    try:
        result = json.loads(ai_reply)
    except json.JSONDecodeError as e:
        raise exceptions.LLMResponseError("The AI response could not be parsed") from e
    return {
        "opening": result['opening'],
        "middle": result['middle'],
        "soft_skills": result['soft_skills'],
        "closing": result['closing']
    }