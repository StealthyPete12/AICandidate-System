import pdfplumber
from docx import Document
import os


def extract_text_from_cv(file_path: str) -> str:
    """Route to the correct parser based on file extension."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CV file not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    else:
        raise ValueError(
            f"Unsupported file type '{ext}'. Use PDF or DOCX."
        )


def extract_text_from_pdf(file_path: str) -> str:
    """Extract all text from a PDF, page by page."""
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def extract_text_from_docx(file_path: str) -> str:
    """Extract all text from a DOCX by joining paragraphs."""
    doc = Document(file_path)
    return "\n".join(p.text for p in doc.paragraphs)
