from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from pydantic import BaseModel

from src.core.models import Role
from src.observability.logging import get_logger
from src.rag.indexing.loader import load_pdf_bytes, load_text
from src.security.rbac import TokenPayload, require_role

logger = get_logger(__name__)
router = APIRouter(prefix="/documents", tags=["documents"])


class IndexResponse(BaseModel):
    document_id: str
    title: str
    chunks: int


@router.post("/index", response_model=IndexResponse)
async def index_document(
    file: UploadFile,
    user: Annotated[TokenPayload, Depends(require_role(Role.editor, Role.admin))],
) -> IndexResponse:
    if file.content_type not in {"application/pdf", "text/plain", "text/markdown"}:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Only PDF, TXT, and MD files are supported.",
        )

    data = await file.read()
    filename = file.filename or "upload"

    if file.content_type == "application/pdf":
        document = load_pdf_bytes(data, filename)
    else:
        from src.core.models import Document
        document = Document(title=filename, content=data.decode("utf-8"), source=filename)

    from src.api.dependencies import get_indexing_pipeline
    pipeline = get_indexing_pipeline()
    chunks = await pipeline.index(document)

    logger.info("document_indexed", doc_id=str(document.id), chunks=len(chunks), user=user.sub)
    return IndexResponse(document_id=str(document.id), title=document.title, chunks=len(chunks))
