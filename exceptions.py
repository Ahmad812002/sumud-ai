class SumudError(Exception):
    """Base class for all expected, domain-level errors."""
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message      # safe, shown to the user
        self.details = details      # for developers, only logged

# documents (the user's file is the problem)
class DocumentError(SumudError): pass
class DuplicateDocumentError(DocumentError): pass
class UnsupportedFileTypeError(DocumentError): pass
class EmptyFileError(DocumentError): pass
class DocumentReadError(DocumentError): pass

# input and users
class InvalidInputError(SumudError): pass
class UserAlreadyExistsError(SumudError): pass

# our own infrastructure
class VectorStoreError(SumudError): pass
class DatabaseError(SumudError): pass

# external providers
class ExternalServiceError(SumudError): pass
class EmbeddingServiceError(ExternalServiceError): pass
class LLMServiceError(ExternalServiceError): pass
class LLMResponseError(LLMServiceError): pass     # empty, cut off, unparsable output
class LLMTimeoutError(LLMServiceError): pass
class LLMUnavailableError(LLMServiceError): pass  # rate limit or provider overload