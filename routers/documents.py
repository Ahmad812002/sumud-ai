from pydantic import BaseModel 
from fastapi import APIRouter, File, HTTPException, UploadFile
from data_access.document_reader import add_embedding
from data_access.db import get_embeddings_collection, get_records, get_profile_collection
import os, shutil, asyncio


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
        raise HTTPException(status_code=500, detail=f"Error occurred while retrieving documents: {str(e)}")


@router.post("/upload_cv")
def upload_cv(file: UploadFile = File(...)):
    try:
        file_location = os.path.join("knowledge_base/cv", file.filename)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"file_name": file.filename, "cv_url": f"/cv/{file.filename}"}
    except HTTPException as e:
        raise e
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ingest_document")
async def ingest_document(file: UploadFile = File(...)):
    try:
        # Get the current maximum ID from the embeddings collection and increment it for the new document
        ids = get_embeddings_collection().get()["ids"]
        doc_id = str(max((int(i) for i in ids), default=0) + 1)
        print("id inside endpoint: ", doc_id)
        os.makedirs("knowledge_base", exist_ok=True)
        file_path = f"knowledge_base/{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return await asyncio.to_thread(add_embedding, file_path, doc_id)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred while ingesting document: {str(e)}")

@router.get("/get_cv")
def get_cv():
    if not os.path.exists("knowledge_base/cv"):
        raise HTTPException(status_code=404, detail="No CV found")
    
    files = os.listdir("knowledge_base/cv")
    pdf_files = [f for f in files if f.endswith('.pdf')]
    
    if not pdf_files:
        raise HTTPException(status_code=404, detail="No CV found")
    
    return {"cv_url": f"/cv/{pdf_files[0]}"}