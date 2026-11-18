import asyncio
import ntpath
import os

import docx
from pypdf import PdfReader
from fastapi import HTTPException
from fastapi.responses import Response
from data_access.embeddings import chunk_text, store_embedding, get_embedding, get_embeddings_collection
import shutil


# reading four types of ducments 
def read_document(document):
    try:
        # Plain string passed directly.
        if not document.endswith(('.pdf', '.txt', '.docx', '.md')):
            return document.strip()  # If it's not a file, treat it as raw text and return it.

        # Text-based documents, read the content and return it as a string.
        if document.endswith(('.txt', '.md')):
            try:
                with open(document, 'r', encoding='utf-8') as f:
                    return f.read().strip()
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error occurred while reading text document: {str(e)}")
        # PDF documents
        if(document.endswith('.pdf')):
            text = ""
            try:
                with open(document, 'rb') as f:

                    reader_pdf = PdfReader(f)
                    for i in range(len(reader_pdf.pages)):
                        page = reader_pdf.pages[i]
                        text += page.extract_text()
                return text.strip()   
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error occurred while reading PDF document: {str(e)}")
        # Word docuements
        if(document.endswith('.docx')):
            try:
                doc = docx.Document(document)
                text = "\n".join([para.text for para in doc.paragraphs])
                return text.strip()
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error occurred while reading Word document: {str(e)}")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found!")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred while reading document: {str(e)}")

# Handleing document, chunk it into smaller pieces, get the embedding of each chunk and store the embedding in the database.
def add_embedding(file_path, file_name, fingerprint, _type):
    try:

        document = read_document(file_path)
        text_chunks = chunk_text(document)

        if(len(os.path.splitext(ntpath.basename(file_name))[1]) == 0):
            raise HTTPException(status_code=401, detail=f"the file has no name")
        if not document.strip():
                raise HTTPException(status_code=422, detail=f"the file is empty") 

        for index, chunk in enumerate(text_chunks):
            if(len(chunk.strip()) < 100):  # Skip chunks that are too short
                    continue
            embedding = get_embedding(chunk)
            

            # prepare chunk_id (doc_id) to be <fingerprint_chunk number> which is chunk_id
            # same as this c9d2d9250a5e7ae4a1482a18aae25de790a6384278e7595c24f789018f6960ba_4
            chunk_id = f"{fingerprint}_{index}"

            if(get_embeddings_collection().get(ids=[chunk_id])['ids']):
                # skip storing if the document is already ingested
                return Response(status_code=409)
            # update store_embedding to include chunk_id, fingerprint and type
            store_embedding(chunk_id, chunk, embedding, source=file_name, fingerprint=fingerprint, _type=_type)


        return Response(201)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Value error: {str(e)}")
    except Exception as e:
        print(f"Error occurred while processing the document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error occurred while processing document: {str(e)}")
