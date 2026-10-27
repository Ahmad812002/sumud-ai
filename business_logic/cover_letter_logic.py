import json
from config.prompts import cover_letter_prompt
from .llm import llm_cover_letter

def run_cover_letter(profile_chunks, job_description, fit_category, matching_points =[], gaps =[], reasoning = ""):
    try:
        language = detect_language(job_description)
        print(language)
        formated_prompt = cover_letter_prompt(
            profile_chunks, 
            fit_category,
            matching_points,
            gaps,
            reasoning,
            language
        )
        cover_letter_response = llm_cover_letter(formated_prompt, job_description)
        # sometimes it returned as lazy object 
        cover_letter_formated_response = format_cover_letter_json(str(cover_letter_response))
        
        if(cover_letter_formated_response['opening'] is not None):
            return {
                        "opening": cover_letter_formated_response['opening'],
                        "middle": cover_letter_formated_response['middle'],
                        "gap": cover_letter_formated_response['gap'],
                        "closing": cover_letter_formated_response['closing']
                    }
    except Exception as e:
        raise ValueError(f"Error occurred while generating cover letter: {str(e)}")


def detect_language(text: str) -> str:
    # Simple detection — check for common German words
    german_indicators = ['die', 'der', 'das', 'und', 'für', 'Sie', 
                         'wir', 'mit', 'von', 'auf', 'Wir', 'suchen',
                         'Stelle', 'Kenntnisse', 'Erfahrung']
    
    text_lower = text.lower()
    german_count = sum(1 for word in german_indicators 
                       if f' {word.lower()} ' in text_lower)
    
    return "German" if german_count >= 3 else "English"
# Fromating ai json response to be more readable 
def format_cover_letter_json(ai_reply):
    try:
        result = json.loads(ai_reply)
        return {
            "opening": result['opening'],
            "middle": result['middle'],
            "gap": result['gap'],
            "closing": result['closing']
        }
    except json.JSONDecodeError:
            raise ValueError(f"LLM returned invalid JSON: {ai_reply}")