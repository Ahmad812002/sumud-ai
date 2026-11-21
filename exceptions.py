
class SumudError(Exception):
    """Base class for all expected, domain-level errors."""

class DocumentError(SumudError):
    pass

class DuplicateDocumentError(DocumentError):
    pass

class EmptyDocumentError(DocumentError):
    pass

class UnsupportedFileTypeError(DocumentError):
    pass

class VectorStoreError(SumudError):
    pass