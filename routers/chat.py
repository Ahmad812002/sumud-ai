from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from config.client import initialize_client
from business_logic.chat_logic import process_chat

# Initialize the OpenAI client with the API key and base URL for OpenRouter.
client = initialize_client()

router = APIRouter()

class ChatRequest(BaseModel):
    message: str


# Handleing assistant mode.
@router.post("/chat")
def chat_bot(request: ChatRequest):
    try:

        reply = process_chat(request.message)
        return reply
    except ValueError as e:
        print(e)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
