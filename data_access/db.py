import exceptions
from clients.supabase_client import get_supabase
from clients.chromadb_client import get_chroma
from main import logger
from supabase_auth.errors import AuthError
from business_logic.auth_logic import translate_auth_error


# here where to connect to DBs supabase/chromadb



def get_preferences_collection():
    try:
        return get_chroma().get_or_create_collection(name="preferences")
    except Exception as e:
        raise RuntimeError(f"Failed to get preferences collection: {str(e)}")   


def get_embeddings_collection():
    try:
        return get_chroma().get_or_create_collection(name="embeddings")
    except Exception as e:
        raise exceptions.ExternalServiceError("Couldn't get embeddings collection") from e

def get_records():
    try:
        collection = get_embeddings_collection().get()
        if(collection is None or 'ids' not in collection or len(collection['ids']) == 0):
            return None
        return collection
    except Exception as e: 
        raise exceptions.ExternalServiceError("Failed to get documents") from e

# Remove every chunk that belongs to one file.
def delete_chunks_by_fingerprint(fingerprint):
    get_embeddings_collection().delete(where={"fingerprint": fingerprint})

# Remove chunks of every CV except the one just stored.
def delete_old_cv_chunks(keep_fingerprint):
    get_embeddings_collection().delete(
        where={"$and": [{"type": "cv"}, {"fingerprint": {"$ne": keep_fingerprint}}]}
    )


# Supabase side
def create_auth_user(email: str, password: str) -> str:
    try:
        res = supabase_client.auth.admin.create_user({
            "email": email.strip().lower(),
            "password": password,
            "email_confirm": True,  # mark as confirmed so they can log in right away
        })
    except AuthError as e:
        raise translate_auth_error(e) from e
    except Exception as e:
        raise exceptions.ExternalServiceError("Sign up failed") from e
    if res.user is None:
        raise exceptions.ExternalServiceError("Sign up failed", details={"reason": "Supabase returned no user"})
    
    return res.user.id

def create_profile(user_id):
    try:
        get_supabase().table("profiles").insert({"id": user_id}).execute()
    except Exception as e:
        try: delete_auth_user(user_id)
        # if the deleting part fails should be deleted manually
        except Exception as e:
            raise exceptions.DatabaseError("Could not create the user profile", details={"reason": f"{type(e).__name__}: {e}", "user_id": user_id}) from e



def delete_auth_user(user_id: str) -> None:
    get_supabase().auth.admin.delete_user(user_id)