import json
import ntpath

from pydantic import BaseModel 
from fastapi import APIRouter, File, HTTPException, UploadFile
from data_access.document_reader import add_embedding
from data_access.db import get_embeddings_collection, get_records
import os, shutil, asyncio
from config.fingerprint import generate_fingerprint


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
    try:
        # updating id parameter to be <fingerprint_chunk number>

        os.makedirs("temporary", exist_ok=True)
        os.makedirs("knowledge_base", exist_ok=True)

        temp_path = f"temporary/{ntpath.basename(file.filename)}"

        with open(temp_path, "wb") as buffer:
            await asyncio.to_thread(shutil.copyfileobj,file.file, buffer)



        # to generate a fingerprint to each file, so that we can check if the document is already ingested or not.
        fingerprint = await asyncio.to_thread(generate_fingerprint, temp_path)

        # updated how endpoint receive a response
        res = await asyncio.to_thread(add_embedding, temp_path, file.filename, fingerprint, "document")
        print("response: ",res)
        file_path = f"knowledge_base/{ntpath.basename(file.filename)}"
        if(res == 201 ):
            await asyncio.to_thread(shutil.move, temp_path, file_path)
        if(res == 409):
            await asyncio.to_thread(os.remove, temp_path)

        return res
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print("Error occurred while ingesting document:", e)
        raise HTTPException(status_code=500, detail=f"Error occurred while ingesting document: {str(e)}")
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
        res = await asyncio.to_thread(add_embedding, temp_file_path, safe_name, fingerprint, "cv")

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