from fastapi import FastAPI, APIRouter, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from requests.help import main
from routers import documents, scorer, chat, cover_letter, preferences
from fastapi.middleware.cors import CORSMiddleware
from exceptions import DuplicateDocumentError, EmptyDocumentError, UnsupportedFileTypeError, SumudError
import os, logging

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
    DuplicateDocumentError: 409,
    EmptyDocumentError: 422,
    UnsupportedFileTypeError: 415,
}

@app.exception_handler(SumudError)
async def sumud_error_handler(request: Request, exc: SumudError):
    status = STATUS_MAP.get(type(exc), 400)
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