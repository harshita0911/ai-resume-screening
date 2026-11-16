
import io
import re
from pathlib import Path

from docx import Document
from pypdf import PdfReader


class ResumeParsingError(Exception):
    """Raised when a resume cannot be parsed."""
    pass


def parse_resume_bytes(file_name: str, content: bytes) -> str:
    """
    Extract readable text from TXT, PDF and DOCX resumes.
    """

    extension = Path(file_name).suffix.lower()

    if not content:
        raise ResumeParsingError(
            f"{file_name} is empty."
        )

    try:

        # TXT FILE
        if extension == ".txt":

            text = content.decode(
                "utf-8-sig",
                errors="replace"
            ).strip()

            if not text:
                raise ResumeParsingError(
                    f"No readable text found in {file_name}."
                )

            return text

        # PDF FILE
        elif extension == ".pdf":

            reader = PdfReader(io.BytesIO(content))

            if reader.is_encrypted:
                raise ResumeParsingError(
                    f"{file_name} is password protected."
                )

            pages_text = []

            for page in reader.pages:
                page_text = page.extract_text() or ""

                if page_text.strip():
                    pages_text.append(page_text)

            text = "\n".join(pages_text).strip()

            if not text:
                raise ResumeParsingError(
                    f"No readable text found in {file_name}. "
                    "The PDF may be scanned or image-based. "
                    "OCR is required to read it."
                )

            return text

        # DOCX FILE
        elif extension == ".docx":

            document = Document(io.BytesIO(content))

            parts = []

            # Read normal paragraphs
            for paragraph in document.paragraphs:

                paragraph_text = paragraph.text.strip()

                if paragraph_text:
                    parts.append(paragraph_text)

            # Read tables
            for table in document.tables:

                for row in table.rows:

                    row_values = []

                    for cell in row.cells:

                        cell_text = cell.text.strip()

                        if cell_text:
                            row_values.append(cell_text)

                    if row_values:
                        parts.append(" | ".join(row_values))

            # Read headers and footers
            for section in document.sections:

                for paragraph in section.header.paragraphs:
                    if paragraph.text.strip():
                        parts.append(paragraph.text.strip())

                for paragraph in section.footer.paragraphs:
                    if paragraph.text.strip():
                        parts.append(paragraph.text.strip())

            text = "\n".join(parts).strip()

            if not text:
                raise ResumeParsingError(
                    f"No readable text found in {file_name}."
                )

            return text

        else:
            raise ResumeParsingError(
                "Only PDF, DOCX and TXT files are supported."
            )

    except ResumeParsingError:
        raise

    except Exception as exc:

        raise ResumeParsingError(
            f"Could not parse {file_name}: {exc}"
        ) from exc


def extract_candidate_profile(
    text: str,
    file_name: str
) -> tuple[str, float]:
    """
    Extract candidate name and experience from resume text.
    """

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    # Candidate name
    name = (
        lines[0]
        if lines
        else Path(file_name).stem
    )

    # Experience detection
    experience = 0.0

    patterns = [

        r"(\d+(?:\.\d+)?)\s*\+?\s*years?\s+(?:of\s+)?experience",

        r"experience\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*years?",

        r"(\d+(?:\.\d+)?)\s*\+?\s*yrs?\s+(?:of\s+)?experience",

        r"(\d+(?:\.\d+)?)\s*\+?\s*years?\s+in\s+",

    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            experience = float(match.group(1))
            break

    return name, experience
