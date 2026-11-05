"""Pattern watch — pure heuristics ported from sovereign PatternRecognition.

Orquestração runtime / Runtime orchestration: funções puras que recebem
listas de eventos/ações (dict) e devolvem diagnósticos; sem estado global
obrigatório, sem classes sovereign. Usadas por witness/agency para
detectar loops, viés e anomalias em ações recentes.

Arquitetura / Architecture: adaptado de
/content/omnimind-kilombo-sovereign/src/metacognition/pattern_recognition.py
(PatternRecognition). Diferenças vs original: funções de módulo (sem classe
nem sensitivity state), sem datetime obrigatório? timestamp mantido para
compatibilidade de saída; numpy não usado (stdlib + math).

Princípios teóricos invocados / Theoretical principles: detecção de
repetição/viés por contagem e entropia de Shannon; anomalias por desvio
padrão; analogia–homologia (interpretativo): padrões repetitivos como
"compulsão de repetição" lacaniana (leitura interpretativa).

pt-BR: vigia de padrões — heurísticas puras sobre listas de eventos.
"""

from __future__ import annotations

import math
from collections import Counter
from datetime import UTC, datetime
from typing import Any


def detect_repetitive_behavior(operations: list[dict[str, Any]], min_reps: int = 2) -> dict[str, Any]:
    """Detect repetitive tool sequences.

    English: Finds tool sequences of length 2..5 repeating >= min_reps+1
    times. Returns dict with patterns list.
    pt-BR: Encontra sequências de ferramentas de tamanho 2..5 repetindo
    >= min_reps+1 vezes.
    """
    if not operations:
        return {"patterns": [], "message": "No operations to analyze"}
    tool_sequences = [op.get("tool_name") for op in operations if op.get("tool_name")]
    if len(tool_sequences) < 3:
        return {"patterns": [], "message": "Insufficient data"}

    patterns = []
    for length in range(2, min(6, len(tool_sequences) // 2 + 1)):
        for i in range(len(tool_sequences) - length):
            sequence = tuple(tool_sequences[i : i + length])
            count = 0
            for j in range(i + length, len(tool_sequences) - length + 1):
                if tuple(tool_sequences[j : j + length]) == sequence:
                    count += 1
            if count >= min_reps:
                patterns.append({"sequence": list(sequence), "repetitions": count + 1, "length": length})

    # dedupe
    seen = set()
    uniq = []
    for p in patterns:
        key = (tuple(p["sequence"]), p["repetitions"])
        if key in seen:
            continue
        seen.add(key)
        uniq.append(p)
    uniq.sort(key=lambda p: p["repetitions"], reverse=True)
    return {"patterns": uniq[:5], "total_patterns": len(uniq), "timestamp": datetime.now(UTC).isoformat()}


def detect_bias(operations: list[dict[str, Any]], sensitivity: float = 0.7) -> dict[str, Any]:
    """Detect tool/agent selection bias.

    English: Flags tools/agents whose usage ratio exceeds sensitivity.
    pt-BR: Marca ferramentas/agentes cuja razão de uso supera sensitivity.
    """
    if not operations:
        return {"biases": [], "message": "No operations to analyze"}
    total = len(operations)
    tool_counts = Counter(str(op.get("tool_name")) for op in operations if op.get("tool_name"))
    agent_counts = Counter(str(op.get("agent")) for op in operations if op.get("agent"))
    biases = []
    for name, count in tool_counts.items():
        ratio = count / total
        if ratio > sensitivity:
            biases.append({"type": "tool", "name": name, "usage_ratio": ratio, "severity": "high" if ratio > 0.8 else "medium"})
    for name, count in agent_counts.items():
        ratio = count / total
        if ratio > sensitivity:
            biases.append({"type": "agent", "name": name, "usage_ratio": ratio, "severity": "high" if ratio > 0.8 else "medium"})
    return {"biases": biases, "total_biases": len(biases), "timestamp": datetime.now(UTC).isoformat()}


def detect_anomalies(operations: list[dict[str, Any]]) -> dict[str, Any]:
    """Detect execution-time and failure-rate anomalies.

    English: Slow executions (> avg + 2*std) and high recent failure rate.
    pt-BR: Execuções lentas (> média + 2*std) e alta taxa de falha recente.
    """
    if not operations:
        return {"anomalies": [], "message": "No operations to analyze"}
    anomalies: list[dict[str, Any]] = []
    times = [op.get("duration", 0) for op in operations if op.get("duration")]
    if times:
        avg = sum(times) / len(times)
        var = sum((t - avg) ** 2 for t in times) / len(times)
        std = var ** 0.5
        threshold = avg + 2 * std
        for op in operations:
            dur = op.get("duration", 0)
            if dur and dur > threshold:
                anomalies.append({
                    "type": "slow_execution",
                    "operation": op.get("tool_name", "unknown"),
                    "duration": dur,
                    "expected": avg,
                    "deviation": (dur - avg) / avg if avg > 0 else 0,
                })
    recent = operations[-10:] if len(operations) >= 10 else operations
    failures = [op for op in recent if not op.get("success", True)]
    if len(failures) >= 5:
        anomalies.append({"type": "high_failure_rate", "failures": len(failures), "total": len(recent), "rate": len(failures) / len(recent)})
    return {"anomalies": anomalies, "total_anomalies": len(anomalies), "timestamp": datetime.now(UTC).isoformat()}


def diversity_score(operations: list[dict[str, Any]]) -> dict[str, Any]:
    """Calculate decision diversity score (0-1).

    English: Shannon entropy of tool distribution normalized by max entropy.
    pt-BR: Entropia de Shannon da distribuição de ferramentas normalizada.
    """
    if not operations:
        return {"diversity_score": 0.0, "message": "No operations to analyze"}
    unique_tools = {str(op.get("tool_name")) for op in operations if op.get("tool_name")}
    unique_agents = {str(op.get("agent")) for op in operations if op.get("agent")}
    counts = Counter(str(op.get("tool_name")) for op in operations if op.get("tool_name"))
    total = sum(counts.values())
    entropy = 0.0
    if total > 0:
        for c in counts.values():
            if c > 0:
                p = c / total
                entropy -= p * math.log2(p)
    max_entropy = math.log2(len(unique_tools)) if len(unique_tools) > 1 else 1.0
    score = min(1.0, entropy / max_entropy) if max_entropy > 0 else 0.0
    if score > 0.7:
        interp = "high"
    elif score > 0.4:
        interp = "medium"
    else:
        interp = "low"
    return {
        "diversity_score": score,
        "unique_tools": len(unique_tools),
        "unique_agents": len(unique_agents),
        "total_operations": len(operations),
        "interpretation": interp,
        "timestamp": datetime.now(UTC).isoformat(),
    }
