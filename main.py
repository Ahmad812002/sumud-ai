from fastapi import FastAPI, APIRouter, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from requests.help import main
from routers import documents, scorer, chat, cover_letter, preferences
from fastapi.middleware.cors import CORSMiddleware
import os, logging, exceptions

app = FastAPI()
router = APIRouter()
logger = logging.getLogger(__name__)

origins = [
    "http://localhost",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    os.environ.get("VITE_BASE_URL"),
    "*"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],

)

# for fresh launching, ensure the cv directory and knowledge_base directory exist for ingesting documents and uploading cv
os.makedirs("knowledge_base/cv", exist_ok=True)
os.makedirs("knowledge_base", exist_ok=True)

app.mount("/cv", StaticFiles(directory="knowledge_base/cv"), name="cv")
app.mount("/knowledge_base", StaticFiles(directory="knowledge_base"), name="knowledge_base")


# instead of repeating try/except in every route, register it here once 
STATUS_MAP = {
    exceptions.SumudError: 400,
    exceptions.DocumentError: 422,
    exceptions.DuplicateDocumentError: 409,
    exceptions.UnsupportedFileTypeError: 415,
    exceptions.EmptyFileError: 400,
    exceptions.DocumentReadError: 404,
    exceptions.InvalidInputError: 400,
    exceptions.VectorStoreError: 503,           # our database is unavailable or failing
    exceptions.EmbeddingServiceError: 502,      # external provider failed
    exceptions.LLMServiceError: 502,
    exceptions.LLMTimeoutError: 504,
    exceptions.LLMResponseError: 501,
    exceptions.LLMUnavailableError: 503,
    exceptions.ExternalServiceError: 502,
}

@app.exception_handler(exceptions.SumudError)
async def sumud_error_handler(request: Request, exc: exceptions.SumudError):
    status = STATUS_MAP.get(type(exc), 400)
    if status >= 500 or exc.__cause__:
        # logs the full chain: "The above exception was the direct cause of..."
        logger.error("%s on %s %s", type(exc).__name__, request.method, request.url.path, exc_info=exc)
    return JSONResponse(status_code=status, content={"detail": str(exc)})


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/")

def root():
    return FileResponse("static/index.html")

app.include_router(scorer.router, prefix="/api/v1", tags=["scorer"])
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(cover_letter.router, prefix="/api/v1", tags=["cover-letter"])
app.include_router(preferences.router, prefix="/api/v1", tags=["preferences"])
app.include_router(documents.router, prefix="/api/v1", tags=["documents"])


if __name__ == "__main__":
    main()