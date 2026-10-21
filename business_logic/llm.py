from config.client import initialize_client
import openai   
from config.prompts import chat_bot_prompt
from business_logic.chat_logic import get_embedding, get_embedding_result



client = initialize_client()

messages_arr = []

# LLM function to generate a job fit score based on the job description and user preferences
def llm_scorer(prompt, job_description):
    try:
        messages_arr = [prompt]
        messages_arr.append({"role": "user", "content": f"Please evaluate this job description: {job_description}"})
        
        response = client.chat.completions.create(
            model="gemini-3.5-flash-lite",
            messages= messages_arr[-10:] ,
            max_tokens=1024,
            response_format={"type": "json_object"},
            temperature=0.0 # For a job fit scorer, reliable scoring, temperature (creativity) should be low
        )
    except openai.APIError as e:
        raise ValueError(f"API Error: {str(e)}")
    except openai.APITimeoutError as e:
        raise ValueError(f"Timeout Error: {str(e)}")
    except openai.APIConnectionError as e:
        raise ValueError(f"API Connection Error: {str(e)}")
    except openai.BadRequestError as e:
        raise ValueError(f"Invalid Request Error (Bad Request): {str(e)}")
    except openai.InternalServerError as e:
        raise ValueError(f"Internal Server Error: {str(e)}")
    except openai.RateLimitError as e:
        raise ValueError(f"Rate Limit Error: {str(e)}")
    except openai.AuthenticationError as e:
        raise ValueError(f"Authentication Error: {str(e)}")

    if response.choices[0].finish_reason == "length":
        return {"error": "Response was cut off. Please try a shorter question."}

    reply = response.choices[0].message.content
    
    if reply is None:
        return {"error": "Could not generate a response. Please try again."}

    return response.choices[0].message.content

# LLM function to generate a cover letter based
def llm_cover_letter(prompt, job_description):
    messages_arr = [prompt]
    messages_arr.append({"role": "user", "content": f"Please evaluate this job description for building the coverletter: {job_description}"})
    try:
        response = client.chat.completions.create(
            model="gemini-3.5-flash-lite",
            messages= messages_arr[-2:],
            max_tokens=2048,
            response_format={"type": "json_object"},
            reasoning_effort="high",
            temperature=1
        )
        messages_arr.append({"role": "user", "content": prompt})
    except openai.APIError as e:
        raise ValueError(f"API Error: {str(e)}")
    except openai.APITimeoutError as e:
        raise ValueError(f"Timeout Error: {str(e)}")
    except openai.APIConnectionError as e:
        raise ValueError(f"API Connection Error: {str(e)}")
    except openai.BadRequestError as e:
        raise ValueError(f"Invalid Request Error (Bad Request): {str(e)}")
    except openai.InternalServerError as e:
        raise ValueError(f"Internal Server Error: {str(e)}")
    except openai.RateLimitError as e:
        raise ValueError(f"Rate Limit Error: {str(e)}")
    except openai.AuthenticationError as e:
        raise ValueError(f"Authentication Error: {str(e)}")
    
    messages_arr.append({"role": "assistant", "content": response.choices[0].message.content})

    if response.choices[0].finish_reason == "length":
        return {"error": "Response was cut off. Please try a shorter question."}

    reply = response.choices[0].message.content
    if reply is None:
        return {"error": "Could not generate a response. Please try again."}

    return response.choices[0].message.content

# LLM function to generate chat_bot
def llm_chat(message):
    chunks = ""
    try:
        #Data preperation

        embedded_vector = get_embedding(message)
        vector_embedding_result = get_embedding_result(embedded_vector, 8)

        if vector_embedding_result is not None:
            chunks = "\n".join([chunk['documents'] for chunk in vector_embedding_result])


        messages_arr = [chat_bot_prompt(chunks)]
        messages_arr.append({"role": "user", "content": message})
        #LLM part
        response = client.chat.completions.create(
            model = "gemini-3.5-flash-lite",
            messages = messages_arr[-10:],
            temperature=1.0, # This is to make the model's response more creative and less deterministic, it will also help the model to provide more diverse responses and avoid repeating the same response.
            reasoning_effort = "high", # This is to make the model put more effort into reasoning and providing a more accurate and relevant response, it will take more time to generate a response but it will be worth it.
            max_tokens=2048,
        )

    except openai.APIError as e:
        raise ValueError(f"API Error: {str(e)}")
    except openai.APITimeoutError as e:
        raise ValueError(f"Timeout Error: {str(e)}")
    except openai.APIConnectionError as e:
        raise ValueError(f"API Connection Error: {str(e)}")
    except openai.BadRequestError as e:
        raise ValueError(f"Invalid Request Error (Bad Request): {str(e)}")
    except openai.InternalServerError as e:
        raise ValueError(f"Internal Server Error: {str(e)}")
    except openai.RateLimitError as e:
        raise ValueError(f"Rate Limit Error: {str(e)}")
    except openai.AuthenticationError as e:
        raise ValueError(f"Authentication Error: {str(e)}")

    messages_arr.append({"role": "assistant", "content": response.choices[0].message.content})
    print(response.choices[0].message.content)
    
    if response.choices[0].finish_reason == "length":
        return {"ai_answer": "Response was cut off. Please try a shorter question."}

    reply = response.choices[0].message.content
    if reply is None:
        return {"ai_answer": "Could not generate a response. Please try again."}

    return {"ai_answer": reply}