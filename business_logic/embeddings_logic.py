import exceptions
from data_access.embeddings import search_embedding, store_embeddings, get_embeddings_collection
from data_access import document_reader
from clients.embedding_client import get_embeddings
from config.settings import THRESHOLD, DEFAULT_N_RESULTS, CHUNK_SIZE, OVERLAP_SIZE



def chunk_text(text):
    # This function applies a simple chunking strategy based on a fixed character limit.
    chunks = []
    for i in range(0, len(text), CHUNK_SIZE - OVERLAP_SIZE): # Move back by overlap_size to create overlap
        chunks.append(text[i:i+CHUNK_SIZE])
    return chunks 

def find_relevant_chunks(query_vector: str, n_results=DEFAULT_N_RESULTS, threshold=THRESHOLD):
    relative_chunks = search_embedding(
                            query_vector,
                            n_results,
                        )
    return [r for r in relative_chunks if r["distance"] <= threshold ]
    
def process_before_store_embedding(file_path, file_name, fingerprint, _type):
    text_document = document_reader.read_document(file_path)
    if(text_document.strip() == ""):
        raise exceptions.EmptyFileError("The file is empty")
        
    chunks = chunk_text(text_document)

    vectors = get_embeddings(chunks)
    # prepare chunk_id (doc_id) to be <fingerprint_chunk number> which is chunk_id
    # same as this c9d2d9250a5e7ae4a1482a18aae25de790a6384278e7595c24f789018f6960ba_4
    ids = [f"{fingerprint}_{i}" for i in range(len(chunks))]

    store_embeddings(ids, chunks, vectors, _source=file_name, _fingerprint=fingerprint, _type=_type)
    return len(ids)
