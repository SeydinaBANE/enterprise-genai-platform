from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from src.api.main import app
from src.core.models import Role
from src.security.rbac import create_token


def _auth(role: Role = Role.editor) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_token('tester', role)}"}


def test_index_txt_file() -> None:
    mock_pipeline = AsyncMock()
    mock_pipeline.index.return_value = [MagicMock(), MagicMock()]

    with patch("src.api.dependencies.get_indexing_pipeline", return_value=mock_pipeline):
        response = TestClient(app).post(
            "/documents/index",
            files={"file": ("notes.txt", b"Hello world document content", "text/plain")},
            headers=_auth(),
        )

    assert response.status_code == 200
    assert response.json()["chunks"] == 2


def test_index_md_file() -> None:
    mock_pipeline = AsyncMock()
    mock_pipeline.index.return_value = [MagicMock()]

    with patch("src.api.dependencies.get_indexing_pipeline", return_value=mock_pipeline):
        response = TestClient(app).post(
            "/documents/index",
            files={"file": ("readme.md", b"# Title\n\nContent", "text/markdown")},
            headers=_auth(),
        )

    assert response.status_code == 200


def test_index_unsupported_type_returns_422() -> None:
    response = TestClient(app).post(
        "/documents/index",
        files={"file": ("data.csv", b"a,b,c", "text/csv")},
        headers=_auth(),
    )
    assert response.status_code == 422


def test_index_requires_editor_role() -> None:
    response = TestClient(app).post(
        "/documents/index",
        files={"file": ("doc.txt", b"content", "text/plain")},
        headers={"Authorization": f"Bearer {create_token('v', Role.viewer)}"},
    )
    assert response.status_code == 403


def test_index_requires_auth() -> None:
    response = TestClient(app).post(
        "/documents/index",
        files={"file": ("doc.txt", b"content", "text/plain")},
    )
    assert response.status_code == 401


def test_index_admin_allowed() -> None:
    mock_pipeline = AsyncMock()
    mock_pipeline.index.return_value = [MagicMock()]

    with patch("src.api.dependencies.get_indexing_pipeline", return_value=mock_pipeline):
        response = TestClient(app).post(
            "/documents/index",
            files={"file": ("doc.txt", b"content", "text/plain")},
            headers=_auth(Role.admin),
        )
    assert response.status_code == 200
