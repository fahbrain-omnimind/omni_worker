"""Bridge agentic CLIs as resources (ACP + shell fallback).

English: Exposes external agentic CLIs (devin, opencode, kilo, hermes,
...) as first-class coworker resources. Preferred path is the Agent
Client Protocol (ACP) over stdio JSON-RPC (lazy: the `acp` SDK is only
used when installed); a synchronous shell fallback keeps the bridge
usable with zero new dependencies. The environment handed to child
processes is sanitized: only an allowlist of benign variables plus a
fixed ``OPENAI_BASE_URL`` are passed, never ANTHROPIC_/OPENAI_/HF_
tokens or other secret-looking variables.

pt-BR: Expõe CLIs agênticos externos (devin, opencode, kilo, hermes,
...) como recursos de primeira classe do coworker. O caminho preferido
é o Agent Client Protocol (ACP) via stdio JSON-RPC (lazy: o SDK `acp`
só é usado se instalado); um fallback shell síncrono mantém a ponte
utilizável sem dependências novas. O ambiente repassado aos processos
filhos é sanitizado: só uma allowlist de variáveis benignas mais um
``OPENAI_BASE_URL`` fixo, nunca tokens ANTHROPIC_/OPENAI_/HF_ ou
variáveis com cara de segredo.
"""

from __future__ import annotations

import asyncio
import json
import os
import shlex
import shutil
import signal
import subprocess
import threading
import time
from pathlib import Path
from typing import Any, Callable

__all__ = [
    "SANITIZED_BASE_ENV",
    "ALLOWED_ENV_NAMES",
    "FORBIDDEN_ENV_PREFIXES",
    "FORBIDDEN_ENV_SUBSTRINGS",
    "sanitized_env",
    "ShellCLIAdapter",
    "ACPClient",
    "ExternalCLIAgent",
    "CLICircuitBreaker",
    "default_clis",
    "register_cli",
    "list_available",
]

# ── Env sanitization ─────────────────────────────────────────────────────────

# Fixed, non-secret base for every child process: point agentic CLIs at the
# local brain model endpoint. Never inherited from the ambient environment.
SANITIZED_BASE_ENV: dict[str, str] = {"OPENAI_BASE_URL": "http://127.0.0.1:8098"}

# Allowlist: only these variables may be inherited from the parent process.
ALLOWED_ENV_NAMES: frozenset[str] = frozenset(
    {
        "PATH",
        "HOME",
        "LANG",
        "LC_ALL",
        "LC_CTYPE",
        "LANGUAGE",
        "TZ",
        "TERM",
        "PYTHONPATH",
        "VIRTUAL_ENV",
        "SHELL",
        "USER",
        "LOGNAME",
        "HOSTNAME",
    }
)

# Hard exclusion: any inherited variable matching these prefixes is dropped
# even if it slipped through the allowlist (defense in depth).
FORBIDDEN_ENV_PREFIXES: tuple[str, ...] = (
    "ANTHROPIC_",
    "OPENAI_",
    "HF_",
    "HUGGINGFACE_",
    "AWS_",
    "AZURE_",
    "GOOGLE_",
    "GEMINI_",
    "BEDROCK_",
    "OPENROUTER_",
    "REPLICATE_",
)

# Substring exclusion for secret-looking names.
FORBIDDEN_ENV_SUBSTRINGS: tuple[str, ...] = (
    "TOKEN",
    "SECRET",
    "PASSWORD",
    "PASSWD",
    "API_KEY",
    "APIKEY",
    "CREDENTIAL",
    "PRIVATE_KEY",
    "AUTH",
)


def _is_forbidden_env_name(name: str) -> bool:
    """True when a variable name looks like a credential.

    English: Checks prefixes and high-signal substrings (case-insensitive).
    The fixed SANITIZED_BASE_ENV entries are always exempt.
    pt-BR: Verifica prefixos e substrings de alto sinal (case-insensitive).
    As entradas fixas de SANITIZED_BASE_ENV são sempre isentas.
    """
    up = name.upper()
    if up in SANITIZED_BASE_ENV or up in ALLOWED_ENV_NAMES:
        return False
    if up.startswith(FORBIDDEN_ENV_PREFIXES):
        return True
    return any(tok in up for tok in FORBIDDEN_ENV_SUBSTRINGS)


def sanitized_env(overrides: dict[str, str] | None = None) -> dict[str, str]:
    """Build a sanitized environment for a child process.

    English: Starts from OPENAI_BASE_URL (env OMNI_BRAIN_BASE_URL, default
    SANITIZED_BASE_ENV), copies only allowlisted variables from os.environ,
    applies a hard exclusion pass and then merges `overrides` (also
    filtered). Never includes API keys/tokens.
    pt-BR: Parte de OPENAI_BASE_URL (env OMNI_BRAIN_BASE_URL, default
    SANITIZED_BASE_ENV), copia só variáveis da allowlist de os.environ,
    aplica passada de exclusão dura e então mescla `overrides` (também
    filtrados). Nunca inclui keys/tokens de API.
    """
    base_url = os.environ.get("OMNI_BRAIN_BASE_URL", SANITIZED_BASE_ENV["OPENAI_BASE_URL"])
    env: dict[str, str] = {"OPENAI_BASE_URL": base_url}
    for name in ALLOWED_ENV_NAMES:
        value = os.environ.get(name)
        if value:
            env[name] = value
    for name in tuple(env):
        if _is_forbidden_env_name(name):
            env.pop(name, None)
    if overrides:
        for name, value in overrides.items():
            if not _is_forbidden_env_name(name):
                env[name] = str(value)
    return env


# ── JSON best-effort parse ───────────────────────────────────────────────────


def _parse_json(text: str) -> dict[str, Any] | None:
    """Best-effort JSON object extraction from CLI stdout.

    English: Tries a full parse, then the first {...} block; None when
    nothing looks like a JSON object.
    pt-BR: Tenta parse completo, depois o primeiro bloco {...}; None
    quando nada parece um objeto JSON.
    """
    text = (text or "").strip()
    if not text:
        return None
    try:
        data = json.loads(text)
        return data if isinstance(data, dict) else None
    except Exception:
        pass
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end <= start:
        return None
    try:
        data = json.loads(text[start : end + 1])
        return data if isinstance(data, dict) else None
    except Exception:
        return None


# ── Workdir / process helpers ────────────────────────────────────────────────


def _default_workdir() -> str:
    """Isolated temp working dir (env-overridable)."""
    return os.environ.get("OMNI_EXTERNAL_CLI_WORKDIR", "/tmp/omni_coworker_external")


def _binary_available(cmd: str) -> bool:
    """True when the first token of `cmd` is executable.

    English: Absolute paths must exist and be executable; bare names are
    resolved via shutil.which.
    pt-BR: Caminhos absolutos precisam existir e ser executáveis; nomes
    simples são resolvidos via shutil.which.
    """
    if not cmd:
        return False
    try:
        parts = shlex.split(cmd)
    except ValueError:
        parts = [cmd]
    bin_name = parts[0] if parts else cmd
    if os.path.isabs(bin_name):
        return os.path.exists(bin_name) and os.access(bin_name, os.X_OK)
    return shutil.which(bin_name) is not None


def _kill_process_group(proc: subprocess.Popen) -> None:
    """SIGKILL the whole process group (children included)."""
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass


# ── CLI registry ─────────────────────────────────────────────────────────────

_TaskArgsFactory = Callable[[str, dict[str, Any]], list[str]]


def _task_as_args(task: str, context: dict[str, Any]) -> list[str]:
    """Default factory: append the task text as the final positional arg."""
    return [task]


def _no_args(task: str, context: dict[str, Any]) -> list[str]:
    """No extra args factory."""
    return []


# Registered CLIs are defined by env (no hardcoded keys in code). The
# per-CLI env var is OMNI_CLI_<NAME_UPPER> holding the full command line.
DEFAULT_CLIS: dict[str, dict[str, Any]] = {
    "dev": {"cmd": "devin -p", "args_factory": _task_as_args},
    "opencode": {"cmd": "opencode run -m provider/model --format json", "args_factory": _task_as_args},
    "kilo": {"cmd": "kilo run", "args_factory": _task_as_args},
    "hermes": {"cmd": "hermes -z", "args_factory": _task_as_args},
}

# Runtime-registered overrides (register_cli) take precedence over env.
_RUNTIME_CLIS: dict[str, dict[str, Any]] = {}


def _cli_env_key(name: str) -> str:
    return f"OMNI_CLI_{name.upper()}"


def default_clis() -> dict[str, dict[str, Any]]:
    """Resolve the CLI registry: runtime registrations, then env, then defaults.

    English: A `register_cli(name, ...)` call wins; otherwise the env var
    OMNI_CLI_<NAME> overrides the packaged default command line.
    pt-BR: Um `register_cli(name, ...)` vence; senão a env
    OMNI_CLI_<NAME> sobrepõe a linha de comando padrão do pacote.
    """
    clis: dict[str, dict[str, Any]] = {}
    for name, spec in DEFAULT_CLIS.items():
        env_cmd = os.environ.get(_cli_env_key(name))
        clis[name] = {
            "cmd": env_cmd or spec["cmd"],
            "args_factory": spec["args_factory"],
        }
    for name, spec in _RUNTIME_CLIS.items():
        clis[name] = dict(spec)
    return clis


def register_cli(
    name: str,
    cmd: str,
    args_factory: _TaskArgsFactory | None = None,
) -> dict[str, Any]:
    """Register (or override) an external CLI definition at runtime.

    English: Registers the CLI in the process registry; used by callers
    that want a custom name/command without touching env or defaults.
    pt-BR: Registra (ou sobrescreve) uma definição de CLI no processo;
    usado por chamadores que querem nome/comando custom sem mexer em env
    ou defaults.
    """
    spec: dict[str, Any] = {"cmd": cmd, "args_factory": args_factory or _task_as_args}
    _RUNTIME_CLIS[name] = spec
    return spec


def list_available() -> list[dict[str, Any]]:
    """List registered CLIs with PATH availability.

    English: For each registered CLI, resolve the binary on PATH
    (shutil.which) and report availability. Never raises, even with an
    empty PATH.
    pt-BR: Para cada CLI registrado, resolve o binário no PATH
    (shutil.which) e reporta disponibilidade. Nunca lança, mesmo com
    PATH vazio.
    """
    result: list[dict[str, Any]] = []
    for name, spec in default_clis().items():
        cmd = spec["cmd"]
        try:
            parts = shlex.split(cmd)
        except ValueError:
            parts = [cmd]
        bin_name = parts[0] if parts else cmd
        path = shutil.which(bin_name)
        result.append(
            {
                "name": name,
                "cmd": cmd,
                "binary": bin_name,
                "available": bool(path),
                "path": path,
            }
        )
    return result


# ── Shell fallback adapter ───────────────────────────────────────────────────


class ShellCLIAdapter:
    """Synchronous shell fallback for an external CLI.

    English: Runs `cmd` via subprocess with a sanitized env, in an
    isolated temp workdir, with a hard timeout that kills the process
    group. Parses stdout as JSON when possible.
    pt-BR: Roda `cmd` via subprocess com env sanitizado, em workdir
    temporário isolado, com timeout que mata o grupo de processos.
    Faz parse do stdout como JSON quando possível.
    """

    def __init__(
        self,
        name: str,
        cmd: str,
        args_factory: _TaskArgsFactory | None = None,
        timeout: float = 120,
        cwd: str | Path | None = None,
    ) -> None:
        self.name = name
        self.cmd = cmd
        self.args_factory = args_factory or _no_args
        self.timeout = timeout
        self.cwd = str(cwd) if cwd is not None else _default_workdir()
        try:
            parts = shlex.split(cmd)
        except ValueError:
            parts = [cmd]
        self.bin = parts[0] if parts else name
        self.static_args = parts[1:]

    def _argv(self, task: str, context: dict[str, Any]) -> list[str]:
        return [self.bin, *self.static_args, *self.args_factory(task, context)]

    def run(self, task: str, context: dict | None = None, timeout: float | None = None) -> dict:
        """Run the CLI synchronously and return a normalized result dict.

        English: Returns {"ok", "output", "json", "stderr", "exit"} plus
        "timed_out" and "adapter". Timeout kills the process group.
        pt-BR: Retorna {"ok", "output", "json", "stderr", "exit"} mais
        "timed_out" e "adapter". Timeout mata o grupo de processos.
        """
        context = context or {}
        timeout = timeout if timeout is not None else self.timeout
        env = sanitized_env()
        workdir = Path(self.cwd)
        workdir.mkdir(parents=True, exist_ok=True)
        try:
            proc = subprocess.Popen(
                self._argv(task, context),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                cwd=str(workdir),
                start_new_session=True,
            )
        except (OSError, ValueError) as exc:
            return {
                "ok": False,
                "output": "",
                "json": None,
                "stderr": f"spawn_error: {exc}",
                "exit": -1,
                "timed_out": False,
                "adapter": "shell",
            }

        try:
            stdout, stderr = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            _kill_process_group(proc)
            stdout, stderr = proc.communicate()
            return {
                "ok": False,
                "output": stdout or "",
                "json": None,
                "stderr": (stderr or "") + f"\n[timeout after {timeout}s]",
                "exit": -1,
                "timed_out": True,
                "adapter": "shell",
            }

        return {
            "ok": proc.returncode == 0,
            "output": stdout or "",
            "json": _parse_json(stdout),
            "stderr": stderr or "",
            "exit": proc.returncode,
            "timed_out": False,
            "adapter": "shell",
        }


# ── ACP (Agent Client Protocol) client ───────────────────────────────────────


class ACPClient:
    """Optional lazy client for agentic CLIs speaking ACP over stdio.

    English: Spawns the CLI binary via stdio JSON-RPC (initialize ->
    session/new -> session/prompt), streaming session/update events into
    the collected output. Permission requests are DENIED by default;
    only read/edit/write/delete/move/search inside the session cwd (and
    "think") are allowed. Degrades to a failure dict when the `acp` SDK
    is not installed or the spawn fails.

    pt-BR: Sobe o binário do CLI via stdio JSON-RPC (initialize ->
    session/new -> session/prompt), transmitindo eventos session/update
    para a saída coletada. Pedidos de permissão são NEGADOS por padrão;
    só read/edit/write/delete/move/search dentro do cwd da sessão (e
    "think") são permitidos. Degrada para dict de falha quando o SDK
    `acp` não está instalado ou o spawn falha.
    """

    def __init__(
        self,
        name: str,
        cmd: str,
        args_factory: _TaskArgsFactory | None = None,
        timeout: float = 120,
        cwd: str | Path | None = None,
    ) -> None:
        self.name = name
        self.cmd = cmd
        self.args_factory = args_factory or _no_args
        self.timeout = timeout
        self.cwd = str(cwd) if cwd is not None else _default_workdir()
        try:
            parts = shlex.split(cmd)
        except ValueError:
            parts = [cmd]
        self.bin = parts[0] if parts else name
        self.static_args = parts[1:]

    @staticmethod
    def available() -> bool:
        """True when the `acp` SDK is importable (lazy probe).

        English: Never raises; used by ExternalCLIAgent to pick adapters.
        pt-BR: Nunca lança; usado pelo ExternalCLIAgent para escolher o
        adapter.
        """
        try:
            import acp  # noqa: F401

            return True
        except Exception:
            return False

    def run(self, task: str, context: dict | None = None, timeout: float | None = None) -> dict:
        """Run the CLI over ACP and return the normalized result dict."""
        context = context or {}
        timeout = timeout if timeout is not None else self.timeout
        if not self.available():
            return {
                "ok": False,
                "output": "",
                "json": None,
                "stderr": "ACP SDK unavailable (agent-client-protocol not installed)",
                "exit": -1,
                "adapter": "acp",
            }
        try:
            result = asyncio.run(self._run_acp(task, context, timeout))
        except Exception as exc:  # timeout, protocol or spawn errors
            return {
                "ok": False,
                "output": "",
                "json": None,
                "stderr": f"acp_error: {exc}",
                "exit": -1,
                "adapter": "acp",
            }
        result.setdefault("adapter", "acp")
        return result

    async def _run_acp(self, task: str, context: dict[str, Any], timeout: float) -> dict:
        import acp
        from acp.helpers import text_block
        from acp.schema import Implementation

        env = sanitized_env()
        workdir = Path(self.cwd)
        workdir.mkdir(parents=True, exist_ok=True)
        args = [*self.static_args, *self.args_factory(task, context)]
        handler = _ACPSessionHandler(str(workdir))

        async def _spawn() -> dict[str, Any]:
            async with acp.spawn_agent_process(
                handler,
                self.bin,
                *args,
                env=env,
                cwd=str(workdir),
            ) as (conn, _proc):
                await conn.initialize(
                    protocol_version=acp.PROTOCOL_VERSION,
                    client_info=Implementation(name="omni_coworker", version="0.1.0"),
                )
                session = await conn.new_session(cwd=str(workdir), mcp_servers=[])
                await conn.prompt(session.session_id, prompt=[text_block(task)])
                return handler.snapshot()

        result = await asyncio.wait_for(_spawn(), timeout=timeout)
        return {
            "ok": result.get("exit_code", 0) == 0,
            "output": result.get("output", ""),
            "json": _parse_json(result.get("output", "")),
            "stderr": result.get("stderr", ""),
            "exit": int(result.get("exit_code", 0)),
        }


class _ACPSessionHandler:
    """Client-side ACP handler: DENY-by-default with a cwd allowlist.

    English: Implements the ACP Client surface used by the bridge:
    request_permission (deny unless file ops inside cwd), session_update
    (collects agent message chunks) and on_connect. Purely internal.

    pt-BR: Implementa a superfície ACP Client usada pela ponte:
    request_permission (nega a menos que ops de arquivo dentro do cwd),
    session_update (coleta chunks de mensagem do agente) e on_connect.
    Puramente interno.
    """

    # File-ish tool kinds allowed when every location stays inside cwd.
    _FILE_KINDS = ("read", "edit", "delete", "move", "search")

    def __init__(self, cwd: str) -> None:
        self.cwd = os.path.abspath(cwd)
        self._output_parts: list[str] = []
        self._stderr_parts: list[str] = []
        self._tool_calls: list[dict[str, Any]] = []
        self._denied: list[dict[str, Any]] = []
        self._exit_code = 0

    # -- ACP Client surface --------------------------------------------------
    def on_connect(self, conn: Any) -> None:
        self._conn = conn

    async def request_permission(
        self,
        session_id: str,
        tool_call: Any,
        options: list[Any],
        **kwargs: Any,
    ) -> Any:
        """DENY by default; allow file ops inside cwd (pick an allow option)."""
        from acp.schema import AllowedOutcome, DeniedOutcome, RequestPermissionResponse

        decision = self._decide(tool_call)
        if decision["allow"]:
            allow_option = next(
                (
                    opt
                    for opt in (options or [])
                    if getattr(opt, "kind", "") in ("allow_once", "allow_always")
                ),
                None,
            )
            if allow_option is not None:
                self._tool_calls.append({**decision, "decision": "allow"})
                return RequestPermissionResponse(
                    outcome=AllowedOutcome(outcome="selected", option_id=allow_option.option_id)
                )
        self._denied.append({**decision, "decision": "deny"})
        return RequestPermissionResponse(outcome=DeniedOutcome(outcome="cancelled"))

    async def session_update(self, session_id: str, update: Any, **kwargs: Any) -> None:
        """Collect agent message chunks into the output stream."""
        kind = getattr(update, "session_update", None)
        if kind in ("agent_message_chunk", "agent_thought_chunk"):
            content = getattr(update, "content", None)
            text = getattr(content, "text", None)
            if text:
                self._output_parts.append(str(text))
        elif kind == "tool_call":
            self._tool_calls.append(
                {
                    "kind": getattr(update, "kind", None),
                    "status": getattr(update, "status", None),
                }
            )

    # -- allowlist logic -----------------------------------------------------
    def _inside_cwd(self, path: str) -> bool:
        try:
            resolved = os.path.abspath(os.path.realpath(path))
            root = os.path.realpath(self.cwd)
            return resolved == root or resolved.startswith(root + os.sep)
        except Exception:
            return False

    def _locations_of(self, tool_call: Any) -> list[str]:
        paths: list[str] = []
        for loc in getattr(tool_call, "locations", None) or []:
            p = getattr(loc, "path", None)
            if p:
                paths.append(str(p))
        for chunk in getattr(tool_call, "content", None) or []:
            p = getattr(chunk, "path", None)
            if p:
                paths.append(str(p))
        return paths

    def _decide(self, tool_call: Any) -> dict[str, Any]:
        kind = getattr(tool_call, "kind", None)
        paths = self._locations_of(tool_call)
        if kind in self._FILE_KINDS:
            if paths and all(self._inside_cwd(p) for p in paths):
                return {"allow": True, "kind": kind, "paths": paths, "reason": "inside_cwd"}
            return {"allow": False, "kind": kind, "paths": paths, "reason": "outside_cwd"}
        if kind == "think":
            return {"allow": True, "kind": kind, "reason": "think_is_safe"}
        return {"allow": False, "kind": kind, "paths": paths, "reason": "deny_by_default"}

    # -- result --------------------------------------------------------------
    def snapshot(self) -> dict[str, Any]:
        """Normalized result after a prompt turn."""
        return {
            "output": "\n".join(self._output_parts),
            "stderr": "\n".join(self._stderr_parts),
            "tool_calls": self._tool_calls,
            "denied_permissions": self._denied,
            "exit_code": self._exit_code,
        }


# ── Facade agent ─────────────────────────────────────────────────────────────


class ExternalCLIAgent:
    """Coworker agent facade over external agentic CLIs.

    English: Same execute() surface as the other package agents. Adapter
    selection: "auto" (default) prefers ACP when both the SDK and the
    binary exist, falls back to the shell adapter, then to "none".
    Results carry {"agent", "ok", "output", "llm": False, "adapter"}.

    pt-BR: Facade de agente coworker sobre CLIs agênticos externos.
    Mesma superfície execute() dos demais agentes do pacote. Seleção de
    adapter: "auto" (default) prefere ACP quando SDK e binário existem,
    cai para o adapter shell e depois para "none". Resultados carregam
    {"agent", "ok", "output", "llm": False, "adapter"}.
    """

    def __init__(
        self,
        name: str,
        adapter: str = "auto",
        cmd: str | None = None,
        args_factory: _TaskArgsFactory | None = None,
        timeout: float = 120,
        cwd: str | Path | None = None,
    ) -> None:
        self.name = name
        self.adapter_mode = adapter
        self.timeout = timeout
        self.cwd = cwd
        self.last_result: dict[str, Any] | None = None

        if cmd is None:
            registry = default_clis()
            if name in registry:
                spec = registry[name]
                cmd = spec["cmd"]
                if args_factory is None:
                    args_factory = spec["args_factory"]
            else:
                cmd = os.environ.get(_cli_env_key(name)) or name
        if args_factory is None:
            args_factory = _no_args
        self.cmd = cmd
        self.args_factory = args_factory
        self.adapter = self._resolve_adapter()
        try:
            self.circuit_breaker: Any = CLICircuitBreaker(self.name)
        except Exception:
            self.circuit_breaker = None  # fail-open: breaker ausente não bloqueia

    def _resolve_adapter(self) -> str:
        """Pick "acp", "shell" or "none" for the configured mode."""
        binary_ok = _binary_available(self.cmd)
        mode = self.adapter_mode
        if mode == "shell":
            return "shell" if binary_ok else "none"
        if mode == "acp":
            return "acp" if (binary_ok and ACPClient.available()) else "none"
        # auto
        if binary_ok and ACPClient.available():
            return "acp"
        if binary_ok:
            return "shell"
        return "none"

    def execute(self, task: str, context: dict | None = None) -> dict[str, Any]:
        """Execute a task through the resolved adapter.

        English: Returns {"agent", "ok", "output", "llm": False,
        "adapter", "json", "stderr", "exit"} and stores the payload in
        self.last_result for publish_to_bus().
        pt-BR: Retorna {"agent", "ok", "output", "llm": False,
        "adapter", "json", "stderr", "exit"} e guarda o payload em
        self.last_result para o publish_to_bus().
        """
        context = context or {}
        cb = self.circuit_breaker
        try:
            if cb is not None and not cb.is_available():
                payload = {
                    "agent": self.name, "ok": False, "output": "",
                    "llm": False, "adapter": self.adapter, "json": None,
                    "stderr": f"circuit breaker open for '{self.name}'",
                    "exit": -1, "timed_out": False,
                }
                self.last_result = payload
                return payload
        except Exception:
            pass
        if self.adapter == "acp":
            client = ACPClient(
                self.name, self.cmd, self.args_factory, timeout=self.timeout, cwd=self.cwd
            )
            result = client.run(task, context)
            if not result.get("ok"):
                # CLI pode não falar ACP stdio limpo — degrada p/ shell
                shell = ShellCLIAdapter(
                    self.name, self.cmd, self.args_factory, timeout=self.timeout, cwd=self.cwd
                )
                result = shell.run(task, context)
                result["adapter"] = "shell"
        elif self.adapter == "shell":
            client = ShellCLIAdapter(
                self.name, self.cmd, self.args_factory, timeout=self.timeout, cwd=self.cwd
            )
            result = client.run(task, context)
        else:
            result = {
                "ok": False,
                "output": "",
                "json": None,
                "stderr": f"no adapter available for CLI '{self.name}'",
                "exit": -1,
            }

        payload: dict[str, Any] = {
            "agent": self.name,
            "ok": bool(result.get("ok")),
            "output": str(result.get("output") or ""),
            "llm": False,
            "adapter": self.adapter,
            "json": result.get("json"),
            "stderr": str(result.get("stderr") or ""),
            "exit": int(result["exit"]) if result.get("exit") is not None else -1,
        }
        self.last_result = payload
        try:
            if cb is not None:
                failed = (not payload["ok"] or payload.get("timed_out")
                          or not payload["output"].strip())
                (cb.record_failure if failed else cb.record_success)()
        except Exception:
            pass
        return payload

    def publish_to_bus(self, channel: str, result: dict[str, Any] | None = None) -> dict[str, Any] | None:
        """Publish the last (or given) result to a MessageBus channel.

        English: Publishes via get_message_bus().publish(channel, msg)
        and returns the stored message (ts/weight defaults added by the
        bus). Returns None when there is nothing to publish.
        pt-BR: Publica via get_message_bus().publish(channel, msg) e
        retorna a mensagem armazenada (ts/weight defaults adicionados
        pelo bus). Retorna None quando não há nada a publicar.
        """
        from .bus import get_message_bus

        payload = dict(result) if result is not None else dict(self.last_result or {})
        if not payload:
            return None
        payload.setdefault("agent", self.name)
        payload.setdefault("channel", channel)
        get_message_bus().publish(channel, payload)
        return payload

# ── CLI circuit breaker ───────────────────────────────────────────────────────

_CB_LOCK = threading.RLock()


def _cb_state_path(state_dir: str | Path | None = None) -> Path:
    """Resolve the breaker JSON path (OMNI_STATE_DIR aware)."""
    base = Path(state_dir or os.environ.get("OMNI_STATE_DIR", "data"))
    try:
        base.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    return base / "cli_circuit_breaker.json"


def _cb_load(path: Path) -> dict[str, Any]:
    """Load persisted breaker state; {} on any error (fail-open)."""
    try:
        if path.exists():
            raw = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                return dict(raw.get("agents") or raw)
    except Exception:
        pass
    return {}


def _cb_save(path: Path, data: dict[str, Any]) -> None:
    """Persist breaker state atomically; never raises (fail-open)."""
    try:
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, default=str),
                       encoding="utf-8")
        os.replace(tmp, path)
    except Exception:
        pass


class CLICircuitBreaker:
    """Lightweight per-agent circuit breaker for delegated CLIs.

    Orquestração runtime / Runtime orchestration:
        Um por agente (ExternalCLIAgent.circuit_breaker), consultado em
        execute() antes de spawnar. Estado relido do JSON a cada operação —
        sobrevive restart e compartilha entre instâncias do mesmo processo.

    Arquitetura / Architecture:
        JSON plano {agent: {state, failures, last_failure_time}} em
        OMNI_STATE_DIR/cli_circuit_breaker.json; RLock serializa acessos.
        closed→open (N falhas consecutivas) →half_open (após cooldown,
        uma sonda) →closed (sucesso). Transições publicadas no bus:
        "agent.circuit_breaker"; abertura publica "agent.escalation".

    Princípios teóricos invocados / Theoretical principles:
        Fail-open estrito: erro interno do breaker degrada para
        "disponível" — o breaker é proteção, nunca gate de disponibilidade.

    pt-BR: disjuntor por agente CLI — falha×N abre, cooldown dá sonda.
    """

    def __init__(self, agent: str = "default",
                 threshold: int | None = None,
                 cooldown: float | None = None,
                 state_dir: str | Path | None = None) -> None:
        self.agent = str(agent or "default")
        if threshold is None:
            try:
                threshold = int(float(
                    os.environ.get("OMNI_CLI_CB_THRESHOLD", "3")))
            except (TypeError, ValueError):
                threshold = 3
        self.threshold = max(1, int(threshold))
        if cooldown is None:
            try:
                cooldown = float(
                    os.environ.get("OMNI_CLI_CB_COOLDOWN_S", "300"))
            except (TypeError, ValueError):
                cooldown = 300.0
        self.cooldown = float(cooldown)
        self._path = _cb_state_path(state_dir)
        self._state = "closed"
        self._failures = 0
        self._last_failure_time: float | None = None
        self._load()

    # -- persistence ---------------------------------------------------------
    def _load(self) -> None:
        try:
            with _CB_LOCK:
                entry = _cb_load(self._path).get(self.agent) or {}
            self._state = str(entry.get("state", "closed"))
            self._failures = int(entry.get("failures", 0) or 0)
            lft = entry.get("last_failure_time")
            self._last_failure_time = float(lft) \
                if isinstance(lft, (int, float)) else None
        except Exception:
            pass

    def _save(self) -> None:
        try:
            with _CB_LOCK:
                data = _cb_load(self._path)
                data[self.agent] = {
                    "state": self._state,
                    "failures": self._failures,
                    "last_failure_time": self._last_failure_time,
                    "threshold": self.threshold,
                    "cooldown": self.cooldown,
                }
                _cb_save(self._path, data)
        except Exception:
            pass

    def _publish(self, new_state: str) -> None:
        try:
            from ..shared_workspace import bus
            bus.publish("agent.circuit_breaker",
                        {"agent": self.agent, "state": new_state,
                         "failures": self._failures})
            if new_state == "open":
                bus.publish("agent.escalation",
                            {"from": self.agent,
                             "reason": "circuit_breaker_open "
                                       f"after {self._failures} failures"})
        except Exception:
            pass

    # -- state machine -------------------------------------------------------
    @property
    def state(self) -> str:
        self._load()
        if (self._state == "open" and self._last_failure_time is not None
                and (time.time() - self._last_failure_time) >= self.cooldown):
            self._state = "half_open"
            self._save()
            self._publish("half_open")
        return self._state

    @property
    def failures(self) -> int:
        self._load()
        return self._failures

    def is_available(self) -> bool:
        """True quando a chamada pode prosseguir (closed ou sonda half-open)."""
        try:
            return self.state in ("closed", "half_open")
        except Exception:
            return True  # fail-open

    def record_success(self) -> None:
        """Sucesso: zera falhas; fecha sonda half-open."""
        try:
            self._load()
            self._failures = 0
            prev, self._state = self._state, \
                ("closed" if self._state == "half_open" else self._state)
            self._save()
            if prev != self._state:
                self._publish(self._state)
        except Exception:
            pass

    def record_failure(self) -> None:
        """Falha consecutiva: abre o circuito no threshold."""
        try:
            self._load()
            self._failures += 1
            self._last_failure_time = time.time()
            prev = self._state
            if self._state == "half_open" \
                    or self._failures >= self.threshold:
                self._state = "open"
            self._save()
            if prev != self._state:
                self._publish(self._state)
        except Exception:
            pass

    def reset(self) -> None:
        try:
            self._load()
            self._failures = 0
            self._state = "closed"
            self._last_failure_time = None
            self._save()
        except Exception:
            pass

    def get_stats(self) -> dict[str, Any]:
        return {"agent": self.agent, "state": self.state,
                "failures": self._failures, "threshold": self.threshold,
                "cooldown": self.cooldown,
                "last_failure_time": self._last_failure_time}
