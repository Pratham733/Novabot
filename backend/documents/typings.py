"""Lightweight typing shim to help the language server understand commonly used fields on Document.
This file is a small helper for Pylance and does not affect runtime.
"""
from typing import Any

class Document:  # pragma: no cover - typing-only
    id: int
    owner: Any
    doc_type: str
    title: str
    content: str
    meta: dict
    created_at: Any
    updated_at: Any
