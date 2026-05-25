import uuid

import pytest

from src.core.models import Document
from src.rag.indexing.chunker import chunk_document


@pytest.fixture
def sample_doc() -> Document:
    return Document(
        id=uuid.uuid4(),
        title="Test Doc",
        content="First paragraph with some content.\n\nSecond paragraph with more content.\n\nThird paragraph.",  # noqa: E501
        source="test.txt",
    )


def test_chunk_document_returns_chunks(sample_doc: Document) -> None:
    chunks = chunk_document(sample_doc, chunk_size=100, overlap=10)
    assert len(chunks) >= 1
    assert all(c.content for c in chunks)


def test_chunk_document_preserves_document_id(sample_doc: Document) -> None:
    chunks = chunk_document(sample_doc, chunk_size=100, overlap=10)
    assert all(c.document_id == sample_doc.id for c in chunks)


def test_chunk_document_sequential_index(sample_doc: Document) -> None:
    chunks = chunk_document(sample_doc, chunk_size=50, overlap=5)
    indices = [c.chunk_index for c in chunks]
    assert indices == list(range(len(chunks)))


def test_chunk_short_document() -> None:
    doc = Document(title="Short", content="Hello world.", source="test.txt")
    chunks = chunk_document(doc, chunk_size=512)
    assert len(chunks) == 1
    assert "Hello world." in chunks[0].content


def test_chunk_empty_document() -> None:
    doc = Document(title="Empty", content="", source="test.txt")
    chunks = chunk_document(doc)
    assert chunks == []
