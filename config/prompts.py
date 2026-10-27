

#Handleing prompt for chat_bot mode



def chat_bot_prompt(chunks):
    system = ''
    print(chunks)
    if(chunks is not None):
        system += f"these are the context to answer: {chunks}"
    system += f"""
        You are a highly precise, knowledgeable, and helpful AI assistant. Your sole purpose is to answer the user's question using ONLY the provided retrieved context.

        [RULES AND CONSTRAINTS]
        1. If context is provided, you must prioritize it in your answer and cite sources, they are metadata in teh context.
        2. If no context is provided, answer helpfully from your own knowledge and tell the user that you don't have enough personalized data.
        3. Do not speculate about facts not in the context or your training, tell the user that you don't have enough personlized data.
    """
    

    return ({"role": "system", "content": system})

# Handleing prompt for job_seeker mode
def job_scorer_prompt(chunks, preferences):    
    # next update plan to use an API text detictor to detect the user's input.

    if chunks:
        candidate_section = f"Candidate Profile:\n{chunks}"
    else:
        candidate_section = "There is no context available, please answer based on your knowledge."
    system_content = f"""
        You are an expert career coach, and interview prep partner use these info to help the user know a job score and if it's matches his career or not.

        {candidate_section}.
        
        User's preferences: {preferences}.

        
        Scoring rubric:
        90-100: meets all requirements, no significant gaps.
        70-89:  meets most requirements, 1-2 minor gaps.
        50-69:  meets core requirements, notable gaps exist.
        below 50: significant misalignment.

        Instructions:
            First analyze the match in detail.
            Then assign a score based only on your analysis above.
            
        Respond only with JSON in this exact structure:
        {{
            "fit_score": "<integer 0-100>",
            "fit_category": "<string>",
            "matching_points": ["<string>"],
            "gaps": ["<string>"],
            "reasoning": "<string>"
        }}
        Rules:
        - Answer depend on the language of the user that he used.
        - Only list a skill as a match if it is explicitly present in the candidate profile. 
        - Do not infer related or adjacent skills.
        - If there is no answer or the input is not job description or you can't handle the input just answer with this respond:
            Sorry! there is no job description please enter a valid one or i couldn't answer you.
        """
    # Here we are returning the system message which will be used as the first message in the conversation, it will set the tone and the context for the rest of the conversation, it will also help the model to understand the user's role and how to respond accordingly.
    return ({"role": "system", "content": system_content})

# Handling cover letter prompt
def cover_letter_prompt(profile_candidate, fit_category, matching_points, gaps, reasoning, language):
    
    scorer_context = ""
    if matching_points and gaps and reasoning:
        scorer_context = f"""
                            Job scorer results:
                            - Fit category: {fit_category}
                            - Matching points: {matching_points}
                            - Gaps: {gaps}
                            - Reasoning: {reasoning}
                        """

    system = f"""You are a cover letter generator. Write entirely in {language}. Do not mix languages.

    Candidate profile: {profile_candidate}
    {scorer_context}

    Generate a cover letter with this exact JSON structure:
    {{
        "opening": "<paragraph>",
        "middle": "<paragraph>",
        "gap": "<paragraph>",
        "closing": "<paragraph>"
    }}

    Rules:
        - opening: who the user is, position, why interested
        - middle: matching points or profile strengths for this role
        - gap: honest acknowledgment of gaps with growth mindset
        - closing: confident call to action
        - Only mention skills explicitly in the profile. Never infer adjacent technologies.
        - Professional, confident, honest tone.
    """

    return {"role": "system", "content": system}

