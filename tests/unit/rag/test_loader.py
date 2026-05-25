from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.rag.indexing.loader import load_file, load_pdf, load_pdf_bytes, load_text


def test_load_text_file(tmp_path: Path) -> None:
    f = tmp_path / "sample.txt"
    f.write_text("Hello world content")
    doc = load_text(f)
    assert doc.content == "Hello world content"
    assert doc.title == "sample"
    assert doc.source == str(f)


def test_load_file_dispatches_txt(tmp_path: Path) -> None:
    f = tmp_path / "readme.txt"
    f.write_text("Read me content")
    doc = load_file(f)
    assert doc.content == "Read me content"


def test_load_file_dispatches_md(tmp_path: Path) -> None:
    f = tmp_path / "notes.md"
    f.write_text("# Heading\n\nBody text")
    doc = load_file(f)
    assert "Heading" in doc.content


def test_load_file_unsupported_raises(tmp_path: Path) -> None:
    f = tmp_path / "data.csv"
    f.write_text("a,b,c")
    with pytest.raises(ValueError, match="Unsupported"):
        load_file(f)


def test_load_pdf_bytes_extracts_text() -> None:
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Page one content"
    mock_reader = MagicMock()
    mock_reader.pages = [mock_page, mock_page]

    with patch("src.rag.indexing.loader.PdfReader", return_value=mock_reader):
        doc = load_pdf_bytes(b"fake-pdf", "report.pdf")

    assert "Page one content" in doc.content
    assert doc.title == "report"
    assert doc.source == "report.pdf"


def test_load_pdf_from_path(tmp_path: Path) -> None:
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "PDF page text"
    mock_reader = MagicMock()
    mock_reader.pages = [mock_page]

    pdf_path = tmp_path / "doc.pdf"
    pdf_path.write_bytes(b"fake")

    with patch("src.rag.indexing.loader.PdfReader", return_value=mock_reader):
        doc = load_pdf(pdf_path)

    assert doc.content == "PDF page text"
    assert doc.title == "doc"


def test_load_file_dispatches_pdf(tmp_path: Path) -> None:
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "PDF content"
    mock_reader = MagicMock()
    mock_reader.pages = [mock_page]

    pdf_path = tmp_path / "doc.pdf"
    pdf_path.write_bytes(b"fake")

    with patch("src.rag.indexing.loader.PdfReader", return_value=mock_reader):
        doc = load_file(pdf_path)

    assert doc.content == "PDF content"
