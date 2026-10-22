from fastapi import FastAPI, APIRouter
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from requests.help import main
from routers import documents, scorer, chat, cover_letter, preferences
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()
router = APIRouter()

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

app.mount("/cv", StaticFiles(directory="knowledge_base/cv"), name="cv")
app.mount("/knowledge_base", StaticFiles(directory="knowledge_base"), name="knowledge_base")

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