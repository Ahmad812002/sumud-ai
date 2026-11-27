import os
from functools import lru_cache
from supabase import create_client, Client
from exceptions import InvalidInputError, ExternalServiceError

# @lru_cache caches only the most recent return value of a function
@lru_cache(maxsize=1)
def get_supabase() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise InvalidInputError("SUPABASE_URL and SUPABASE_KEY must be set in .env")
    try:
        return create_client(url, key)
    except Exception as e:
        raise ExternalServiceError("Can't connect to Supabase") from e