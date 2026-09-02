import io
import re

from docx import Document
from pypdf import PdfReader


class ResumeParsingError(Exception):
    pass


def parse_resume_bytes(file_name: str, content: bytes) -> str:
    extension = file_name.lower().split(".")[-1]

    try:
        if extension == "txt":
            return content.decode("utf-8", errors="ignore").strip()

        if extension == "pdf":
            reader = PdfReader(io.BytesIO(content))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            return text.strip()

        if extension == "docx":
            document = Document(io.BytesIO(content))
            text = "\n".join(paragraph.text for paragraph in document.paragraphs)
            return text.strip()

    except Exception as exc:
        raise ResumeParsingError(f"Could not parse {file_name}: {exc}") from exc

    raise ResumeParsingError("Only PDF, DOCX and TXT files are supported.")


def extract_candidate_profile(text: str, file_name: str) -> tuple[str, float]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    name = lines[0] if lines else file_name.rsplit(".", 1)[0]

    experience = 0.0
    patterns = [
        r"(\d+(?:\.\d+)?)\s*\+?\s*years?\s+(?:of\s+)?experience",
        r"experience\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*years?",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            experience = float(match.group(1))
            break

    return name, experience