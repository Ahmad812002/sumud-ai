from supabase_auth.errors import AuthError
import exceptions
from data_access import db
import logging

logger = logging.getLogger(__name__)


def sign_up_user(email: str, password: str) -> str:
    user_id = db.create_auth_user(email, password)
    try: 
        db.create_profile_user(user_id)
    except exceptions.DatabaseError:
        try:
            db.delete_auth_user(user_id)
        except Exception:
            logger.critical("Orphan auth user, delete manually: %s", user_id, exc_info=True)
        raise
    return user_id

def translate_auth_error(e: AuthError) -> exceptions.SumudError:
    code = getattr(e, "code", None)            # check what your supabase version exposes
    print("trnaslate_auth_error: ", code)
    if code in ("email_exists", "user_already_exists"):
        return exceptions.UserAlreadyExistsError("An account with this email already exists")
    if code == "weak_password":
        return exceptions.InvalidInputError("The password does not meet the requirements")
    return exceptions.ExternalServiceError("Sign up failed", details={"reason": str(e)})
