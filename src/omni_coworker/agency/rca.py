"""RCA-lite — lightweight dependency graph + causal trace for worker modules.

Orquestração runtime / Runtime orchestration: mantém um grafo de
dependências editável (`dependency_graph` dict) e um registro de falhas
(`register_failure`). `trace_root_cause(failure_id)` retorna o caminho
causal (BFS) a partir da falha até a(s) causa(s) raiz, seguindo arestas
de dependência.

Arquitetura / Architecture: adaptado de
/content/omnimind-kilombo-sovereign/src/metacognition/root_cause_analysis.py
(DependencyGraph + RootCauseEngine). Diferenças vs original: sem classes
sovereign/ComponentType/FailureType; grafo representado como dict
mutável component_id -> set(dependencies); interface mínima; algoritmo de
trace extraído (BFS causal path), não a classe RootCauseEngine inteira.

Princípios teóricos invocados / Theoretical principles: rastreamento
causal via travessia em grafo (BFS) sobre dependências; analogia–homologia
(interpretativo): cadeia causal como "cadeia significante" (leitura
interpretativa).

pt-BR: RCA leve — grafo de dependências + trace causal BFS.
"""

from __future__ import annotations

from collections import deque
from typing import Any


class RCA:
    """Lightweight RCA container."""

    def __init__(self) -> None:
        self.dependency_graph: dict[str, set[str]] = {}
        self._failures: dict[str, dict[str, Any]] = {}
        self._order: list[str] = []

    def add_component(self, component: str, dependencies: list[str] | None = None) -> None:
        self.dependency_graph.setdefault(component, set())
        for d in dependencies or []:
            self.dependency_graph.setdefault(d, set())
            self.dependency_graph[component].add(d)

    def remove_dependency(self, frm: str, to: str) -> None:
        if frm in self.dependency_graph:
            self.dependency_graph[frm].discard(to)

    def register_failure(self, component: str, cause: str, ts: Any) -> str:
        fid = f"{component}:{len(self._failures)}"
        self._failures[fid] = {"id": fid, "component": component, "cause": cause, "ts": ts}
        self._order.append(fid)
        self.dependency_graph.setdefault(component, set())
        return fid

    def trace_root_cause(self, failure_id: str) -> list[str]:
        """BFS trace from failed component to root causes (leaves).

        English: Walks dependency edges from the failed component outward,
        returning the path component ids from failure to root (deepest
        dependency). Returns [] if failure unknown.
        pt-BR: Percorre arestas de dependência da falha à raiz.
        """
        f = self._failures.get(failure_id)
        if not f:
            return []
        start = f["component"]
        # BFS to find deepest dependency chain
        # Build path via parent tracking
        visited: set[str] = set()
        parent: dict[str, str | None] = {start: None}
        queue: deque[str] = deque([start])
        farthest = start
        while queue:
            cur = queue.popleft()
            if cur in visited:
                continue
            visited.add(cur)
            farthest = cur
            for dep in self.dependency_graph.get(cur, ()):
                if dep not in visited and dep not in parent:
                    parent[dep] = cur
                    queue.append(dep)
        # reconstruct path from farthest back to start
        path: list[str] = []
        cur: str | None = farthest
        while cur is not None:
            path.append(cur)
            cur = parent.get(cur)
        path.reverse()
        if path and path[0] != start:
            path = [start] + [p for p in path if p != start]
        # ensure start first
        if not path or path[0] != start:
            path = [start] + path
        # dedupe preserving order
        seen: set[str] = set()
        out: list[str] = []
        for p in path:
            if p in seen:
                continue
            seen.add(p)
            out.append(p)
        return out


# module-level default instance + helpers
_DEFAULT = RCA()


def register_failure(component: str, cause: str, ts: Any) -> str:
    return _DEFAULT.register_failure(component, cause, ts)


def trace_root_cause(failure_id: str) -> list[str]:
    return _DEFAULT.trace_root_cause(failure_id)


def get_dependency_graph() -> dict[str, set[str]]:
    return _DEFAULT.dependency_graph
