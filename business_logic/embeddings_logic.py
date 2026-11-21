import ntpath
import os
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from data_access.embeddings import search_embedding, store_embedding, get_embeddings_collection
from data_access import document_reader
from clients import embedding_client
from config.settings import RELEVANCE_MAX_DISTANCE, DEFAULT_N_RESULTS, CHUNK_SIZE, OVERLAP_SIZE




def chunk_text(text):
    # This function applies a simple chunking strategy based on a fixed character limit.
    
    chunks = []
    try:
        for i in range(0, len(text), CHUNK_SIZE - OVERLAP_SIZE): # Move back by overlap_size to create overlap
            chunks.append(text[i:i+CHUNK_SIZE])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred while chunking text: {e}")
    return chunks 

def find_relevant_chunks(text: str, n_results: int = DEFAULT_N_RESULTS):
    query_vector = embedding_client.get_embedding(text)
    return search_embedding(
        query_vector,
        n_results,
        max_distance=RELEVANCE_MAX_DISTANCE,
    )

def process_before_store_embedding(file_path, file_name, fingerprint, _type):
    try:

        document = document_reader.read_document(file_path)
        text_chunks = chunk_text(document)

        if(len(os.path.splitext(ntpath.basename(document))[1]) == 0):
            raise HTTPException(status_code=401, detail=f"the file has no name")
        with open(document, 'r', encoding='utf-8') as f:
            if(len(f.read().strip()) == 0):
                raise HTTPException(status_code=403, detail=f"the file is empty") 

        for index, chunk in enumerate(text_chunks):
            if(len(chunk.strip()) < 100):  # Skip chunks that are too short
                    continue
            embedding = embedding_client.get_embedding(chunk)

            # prepare chunk_id (doc_id) to be <fingerprint_chunk number> which is chunk_id
            # same as this c9d2d9250a5e7ae4a1482a18aae25de790a6384278e7595c24f789018f6960ba_4
            chunk_id = f"{fingerprint}_{index}"

            if(get_embeddings_collection().get(ids=[chunk_id])['ids']):
                # skip storing if the document is already ingested
                return JSONResponse(status_code=409, content={"message": f"A document with the name {file_name} is already ingested. or the database has same records."})
            # update store_embedding to include chunk_id, fingerprint and type
            store_embedding(chunk_id, chunk, embedding, source=file_name, fingerprint=fingerprint, _type=_type)

        return JSONResponse(status_code=201, content={"message": "Document ingested successfully"})
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Value error: {str(e)}")
    except Exception as e:
        print(f"Error occurred while processing the document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error occurred while reading document: {str(e)}")
