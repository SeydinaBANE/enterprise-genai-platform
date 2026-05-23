from __future__ import annotations

import io
from pathlib import Path

from pypdf import PdfReader

from src.core.models import Document
from src.observability.logging import get_logger

logger = get_logger(__name__)


def load_pdf(path: Path) -> Document:
    reader = PdfReader(str(path))
    pages = [page.extract_text() or "" for page in reader.pages]
    content = "\n\n".join(pages)
    logger.info("pdf_loaded", path=str(path), pages=len(pages), chars=len(content))
    return Document(title=path.stem, content=content, source=str(path))


def load_text(path: Path) -> Document:
    content = path.read_text(encoding="utf-8")
    logger.info("text_loaded", path=str(path), chars=len(content))
    return Document(title=path.stem, content=content, source=str(path))


def load_pdf_bytes(data: bytes, filename: str) -> Document:
    reader = PdfReader(io.BytesIO(data))
    pages = [page.extract_text() or "" for page in reader.pages]
    content = "\n\n".join(pages)
    name = Path(filename).stem
    logger.info("pdf_bytes_loaded", filename=filename, pages=len(pages))
    return Document(title=name, content=content, source=filename)


def load_file(path: Path) -> Document:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return load_pdf(path)
    if suffix in {".txt", ".md"}:
        return load_text(path)
    raise ValueError(f"Unsupported file type: {suffix}")
