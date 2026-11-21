from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from config.client import initialize_client
from business_logic.chat_logic import process_chat, process_chat_stream
import json
import asyncio

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


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    async def event_generator():
        try:
            for chunk in process_chat_stream(request.message):
                if chunk:
                    yield f"data: {json.dumps({'delta': chunk}, ensure_ascii=False)}\n\n"
                    await asyncio.sleep(0)
            yield "data: [DONE]\n\n"
        except Exception as e:
            print(e)
            error = json.dumps({"error": str(e)}, ensure_ascii=False)
            yield f"data: {error}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
