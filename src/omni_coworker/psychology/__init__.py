"""psychology — módulos psicológicos portados do sovereign (CPU/RAM).

pt-BR: subset portado de src/psychology (OW-STU-008b). Começa com
scars (integração de trauma → regras de defesa permanentes).
"""

from .scars import TraumaIntegration, get_scars

__all__ = ["TraumaIntegration", "get_scars"]
