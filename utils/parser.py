from pathlib import Path
from typing import Union

PathLike = Union[str, Path]


def parse_pdf(path: PathLike) -> str:
    import pdfplumber

    text_chunks = []
    with pdfplumber.open(str(path)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            if page_text.strip():
                text_chunks.append(page_text.strip())
    return "\n\n".join(text_chunks).strip()


def parse_docx(path: PathLike) -> str:
    from docx import Document

    doc = Document(str(path))
    lines = [paragraph.text.strip() for paragraph in doc.paragraphs if paragraph.text.strip()]
    return "\n".join(lines).strip()


def parse_text(path: PathLike) -> str:
    return Path(path).read_text(encoding="utf-8").strip()


def parse_resume(path: PathLike) -> str:
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(f"Resume file not found: {source}")

    suffix = source.suffix.lower()
    if suffix == ".pdf":
        parsed = parse_pdf(source)
    elif suffix == ".docx":
        parsed = parse_docx(source)
    elif suffix in {".txt", ".md"}:
        parsed = parse_text(source)
    else:
        raise ValueError(
            f"Unsupported resume format '{suffix}'. Use .pdf, .docx, .txt, or .md."
        )

    if not parsed:
        raise ValueError(f"No text could be extracted from {source}")
    return parsed
