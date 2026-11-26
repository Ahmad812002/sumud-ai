import docx
from pypdf import PdfReader
import exceptions
from pathlib import Path

def _read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")

def _read_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    if reader.is_encrypted:
        raise exceptions.DocumentReadError("The PDF is password-protected")
    return "\n".join((page.extract_text() or "") for page in reader.pages)

def _read_docx(path: Path) -> str:
    doc = docx.Document(str(path))
    return "\n".join(p.text for p in doc.paragraphs)

READERS = {
    ".txt": _read_text_file,
    ".md": _read_text_file,
    ".pdf": _read_pdf,
    ".docx": _read_docx,
}

def read_document(document) -> str:
    path = Path(document)                      # accepts str or Path
    reader = READERS.get(path.suffix.lower())
    if reader is None:
        raise exceptions.UnsupportedFileTypeError(
            f"Unsupported file type: {path.suffix or 'none'}"
        )
    try:
        return reader(path).strip()
    except exceptions.SumudError:
        raise                                   # keep our own messages (e.g. password-protected)
    except Exception as e:
        raise exceptions.DocumentReadError(f"Could not read the {path.suffix} document") from e
