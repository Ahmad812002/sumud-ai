class SumudError(Exception):
    """Base class for all expected, domain-level errors."""
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details

# --- documents (user's file is the problem) ---
class DocumentError(SumudError): pass
class DuplicateDocumentError(DocumentError): pass
class UnsupportedFileTypeError(DocumentError): pass
class EmptyFileError(DocumentError): pass
class DocumentReadError(DocumentError): pass
# --- input ---
class InvalidInputError(SumudError): pass

# --- infrastructure (our systems or providers are the problem) ---
class VectorStoreError(SumudError): pass
class SearchVectorError(SumudError): pass
class EmbeddingServiceError(SumudError): pass
class LLMServiceError(SumudError): pass