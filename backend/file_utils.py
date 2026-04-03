import io
import PyPDF2
import docx

def extract_text_from_file(file_bytes: bytes, filename: str) -> tuple[str, str]:
    """Returns (extracted_text, file_type)"""
    name_lower = filename.lower()

    if name_lower.endswith(".pdf"):
        return _extract_pdf(file_bytes), "pdf"
    elif name_lower.endswith(".docx"):
        return _extract_docx(file_bytes), "docx"
    elif name_lower.endswith(".txt") or name_lower.endswith(".md"):
        return file_bytes.decode("utf-8", errors="ignore"), "txt"
    else:
        # Try decoding as plain text
        try:
            return file_bytes.decode("utf-8", errors="ignore"), "txt"
        except:
            raise ValueError(f"Unsupported file type: {filename}")

def _extract_pdf(file_bytes: bytes) -> str:
    reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    texts = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            texts.append(text)
    return "\n".join(texts)

def _extract_docx(file_bytes: bytes) -> str:
    doc = docx.Document(io.BytesIO(file_bytes))
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
