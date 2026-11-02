"""Soul: API and static assets (Machine Public Soul).

English: FastAPI routes and i18n static files.
pt-BR: Rotas FastAPI e arquivos estáticos i18n.
"""

from __future__ import annotations

from . import api
from .api import router

__all__ = ["api", "router"]
