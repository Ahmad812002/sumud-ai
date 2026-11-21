import docx
from pypdf import PdfReader
from fastapi import HTTPException


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
        raise HTTPException(status_code=404, detail=f"File not found: {document}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred while reading document: {str(e)}")
