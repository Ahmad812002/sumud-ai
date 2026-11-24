from clients import client
import openai, logging
import exceptions

_client = client.initialize_client()
messages_arr = []

logger = logging.getLogger(__name__)

_client = client.initialize_client()
MODEL = "gemini-3.5-flash-lite"


def _details(feature: str, e: Exception) -> dict:
    return {"feature": feature, "reason": f"{type(e).__name__}: {e}"}


def _call_llm(feature: str, **kwargs) -> str:
    """The only place that talks to the provider. Every failure becomes one of our exceptions."""
    try:
        response = _client.chat.completions.create(model=MODEL, timeout=60, **kwargs)
    
    except openai.APITimeoutError as e:        # most specific first
        raise exceptions.LLMTimeoutError("The AI service took too long to respond", details=_details(feature, e)) from e

    except openai.RateLimitError as e:
            raise exceptions.LLMUnavailableError("The AI service is busy, please try again shortly", details=_details(feature, e)) from e

    except openai.InternalServerError as e:       # provider overloaded or failing (5xx)
            raise exceptions.LLMUnavailableError("The AI service is temporarily unavailable, please try again", details=_details(feature, e)) from e

    except openai.AuthenticationError as e:    # our API key/config problem, not the user's
            raise exceptions.LLMServiceError("The AI service is not configured correctly", details=_details(feature, e)) from e

    except openai.APIError as e:               # base class last: everything else from the SDK
            raise exceptions.LLMServiceError("The AI service failed", details=_details(feature, e)) from e

    if not response.choices:
        raise exceptions.LLMResponseError("The AI service returned no result", details={"feature": feature})

    choice = response.choices[0]
    logger.info("LLM %s usage: %s", feature, response.usage)    # token counts only

    if choice.finish_reason == "length":
        raise exceptions.LLMResponseError("The AI response was cut off", details={"feature": feature, "usage": str(response.usage)})
    if not choice.message.content:
        raise exceptions.LLMResponseError("The AI service returned an empty response", details={"feature": feature})
    return choice.message.content





# LLM function to generate a job fit score based on the job description and user preferences
def llm_scorer(prompt, job_description) -> str:
    return _call_llm(
        "scorer",
        messages=[prompt, {"role": "user", "content": f"Please evaluate this job description: {job_description}"}],
        max_tokens=1024,
        response_format={"type": "json_object"},
        temperature=0.0,          # reliable scoring needs low creativity
    )

# LLM function to generate a cover letter based
def llm_cover_letter(prompt, job_description) -> str:
    return _call_llm(
        "cover_letter",
        messages=[prompt, {"role": "user",
                           "content": f"Please evaluate this job description for building the coverletter: {job_description}"}],
        max_tokens=4096,
        response_format={"type": "json_object"},
        reasoning_effort="high",
        temperature=1,
    )


# LLM function to generate chat_bot
def llm_chat(prompt, message) -> str:
    return _call_llm(
        "chat",
        messages=[prompt, {"role": "user", "content": message}],
        max_tokens=2048,
        reasoning_effort="high",
        temperature=1.0,
    )