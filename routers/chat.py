from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from config.client import initialize_client
from business_logic.llm import llm_chat

# Initialize the OpenAI client with the API key and base URL for OpenRouter.
client = initialize_client()

router = APIRouter()

class ChatRequest(BaseModel):
    message: str


# Handleing assistant mode.
@router.post("/chat")
def chat_bot(request: ChatRequest):
    try:
        reply = llm_chat(request.message)
        return {"ai_answer": reply}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:      
        raise HTTPException(status_code=500, detail=str(e))
