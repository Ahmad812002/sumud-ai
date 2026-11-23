from pydantic import BaseModel
from fastapi import APIRouter
from clients.client import initialize_client
from business_logic.chat_logic import process_chat
from exceptions import ChatServiceError

# Initialize the OpenAI client with the API key and base URL for OpenRouter.
client = initialize_client()

router = APIRouter()

class ChatRequest(BaseModel):
    message: str


# Handleing assistant mode.
@router.post("/chat")
def chat_bot(request: ChatRequest):
    reply = process_chat(request.message)
    return reply
