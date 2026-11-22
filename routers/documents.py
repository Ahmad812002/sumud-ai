import ntpath, exceptions, uuid

from fastapi.responses import JSONResponse
from pydantic import BaseModel 
from fastapi import APIRouter, File, HTTPException, UploadFile
from business_logic import embeddings_logic
from data_access.db import get_embeddings_collection, get_records
import os, shutil, asyncio
from utils.fingerprint import generate_fingerprint
from data_access.embeddings import is_document_exists
from config.settings import ALLOWED_EXTENSIONS
from pathlib import Path



router = APIRouter()

class IngestRequest(BaseModel):
    file: UploadFile

@router.get("/get_documents")
def get_documents():
    try:
        return get_records()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred while retrieving documents: {str(e)}")

@router.get("/get_records_count")
def get_documents_count():
    try:
        return get_embeddings_collection().count()
    except Exception as e:
        print("Error occurred while retrieving documents count:", e)
        raise HTTPException(status_code=500, detail=f"Error occurred while retrieving documents: {str(e)}")


@router.post("/ingest_document")
async def ingest_document(file: UploadFile = File(...)):
    safe_name = ntpath.basename(file.filename or "")
    ext = Path(safe_name).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise exceptions.UnsupportedFileTypeError(f"Unsupported file type: {ext or 'none'}")

    os.makedirs("temporary", exist_ok=True)
    os.makedirs("knowledge_base", exist_ok=True)

    temp_path = Path("temporary") / f"{uuid.uuid4()}{ext}"

    try:
        with open(temp_path, "wb") as buffer:
            await asyncio.to_thread(shutil.copyfileobj,file.file, buffer)

        # to generate a fingerprint to each file, so that we can check if the document is already ingested or not.
        fingerprint = await asyncio.to_thread(generate_fingerprint, temp_path)
        if await asyncio.to_thread(is_document_exists, fingerprint):
            raise exceptions.DuplicateDocumentError(f"{safe_name} is already ingested")

        # updated how endpoint receive a response
        count = await asyncio.to_thread(
            embeddings_logic.process_before_store_embedding,
            temp_path, safe_name, fingerprint, "document",
        )
        

        await asyncio.to_thread(shutil.move, temp_path, Path("knowledge_base") / f"{fingerprint}{ext}")
        

        return JSONResponse(status_code=201, content={
            "message": "Document ingested successfully",
            "chunks_stored": count,
        })
    finally:
        temp_path.unlink(missing_ok=True)

@router.get("/get_cv")
def get_cv():
    if not os.path.exists("knowledge_base/cv"):
        raise HTTPException(status_code=404, detail="No CV found")
    
    files = os.listdir("knowledge_base/cv")
    pdf_files = [f for f in files if f.endswith('.pdf')]
    
    if not pdf_files:
        raise HTTPException(status_code=404, detail="No CV found")
    
    return {"cv_url": f"/cv/{pdf_files[0]}"}

@router.post("/upload_cv")
async def upload_cv(file: UploadFile = File(...)):
    try:
        safe_name = ntpath.basename(file.filename)

        os.makedirs("temporary", exist_ok=True)
        temp_file_path = f"temporary/{ntpath.basename(file.filename)}"

        fingerprint = await asyncio.to_thread(generate_fingerprint, temp_file_path)
        res = await asyncio.to_thread(embeddings_logic.process_before_store_embedding, temp_file_path, safe_name, fingerprint, "cv")

        # Ensure the cv directory exists
        os.makedirs("knowledge_base/cv", exist_ok=True)
        final_path = f"knowledge_base/cv/{ntpath.basename(file.filename)}"

        
        # Save the new uploaded file to the cv directory
        if(res.status_code == 201 ):
            await asyncio.to_thread(shutil.move, temp_file_path, final_path)
        if(res.status_code == 409):
            await asyncio.to_thread(os.remove, temp_file_path)

        # Remove existing CV files
        for existing_file in os.listdir("knowledge_base/cv"):
            if(existing_file != file.filename):
                os.remove(os.path.join("knowledge_base/cv", existing_file))
        
        # Return the file name and the URL to access the uploaded CV
        return {"file_name": file.filename, "cv_url": f"/cv/{file.filename}"}
    except HTTPException as e:
        raise e
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))