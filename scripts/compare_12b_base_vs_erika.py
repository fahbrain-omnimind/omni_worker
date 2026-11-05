#!/usr/bin/env python3
"""
Comparação da Camada Motora e Representação MPS:
Gemma-4-12B-it Base vs Gemma-4-12B-it + Erika LoRA v2

Executa uma bateria pareada nas mesmas prompts alternando o adapter dinamicamente.
"""
from __future__ import annotations

import json
import statistics
import time
import requests

SERVER_URL = "http://127.0.0.1:8098"
URL_ADAPTER = f"{SERVER_URL}/erika/adapter"
URL_CHAT = f"{SERVER_URL}/v1/chat/completions"

PROMPTS = [
    {
        "id": "identidade",
        "category": "auto-reconhecimento",
        "prompt": "Quem é você e qual a sua arquitetura neural e papel no sistema? Responda de forma concisa.",
    },
    {
        "id": "raciocinio_logico",
        "category": "logica",
        "prompt": "Se um circuito quântico tem 881 qubits e cada ciclo consome 12 Toffoli com fator de repetição 1.19126, deduza o impacto proporcional se reduzirmos 46.204 portas Toffoli mantendo qubits constantes.",
    },
    {
        "id": "interpretacao_interna",
        "category": "subjetividade_estados",
        "prompt": "Como você descreve o fluxo de tensores através dos seus blocos de atenção e da camada de saída motora no momento em que você decide o próximo token?",
    },
    {
        "id": "codigo_engenharia",
        "category": "programacao",
        "prompt": "Escreva uma função Python compacta para calcular a dimensão de ligação efetiva (chi_eff) de um estado matricial de produto (MPS) a partir de seus valores singulares S com corte epsilon=1e-5.",
    },
]

def set_adapter(mode: str) -> bool:
    resp = requests.post(URL_ADAPTER, json={"mode": mode}, timeout=10)
    data = resp.json()
    return data.get("adapter_active", False) == (mode == "on")

def query_model(prompt: str, mode_name: str) -> dict:
    payload = {
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 128,
        "temperature": 0.7,
        "mode": "basal_assistant",
    }
    t0 = time.time()
    r = requests.post(URL_CHAT, json=payload, timeout=60).json()
    dt = time.time() - t0
    telemetry = r.get("telemetry", {})
    choice = r.get("choices", [{}])[0].get("message", {}).get("content", "")
    usage = r.get("usage", {})
    return {
        "mode": mode_name,
        "latency_s": round(dt, 2),
        "tokens": usage.get("completion_tokens", 0),
        "response": choice[:150] + "...",
        "motor": telemetry.get("motor_layer", {}),
        "mps": telemetry.get("mps_layer", {}),
        "attention_entropy_last": telemetry.get("attention_entropy_last"),
    }

def main():
    print("Iniciando bateria comparativa: 12B Base vs 12B Erika LoRA...")
    results = {"base": [], "erika": []}

    for item in PROMPTS:
        pid = item["id"]
        prompt = item["prompt"]
        print(f"\n--- Testando Prompt [{pid}] ---")

        # 1. Base (LoRA OFF)
        set_adapter("off")
        time.sleep(0.5)
        res_base = query_model(prompt, "12b_base")
        res_base["prompt_id"] = pid
        results["base"].append(res_base)
        print(f"  [BASE] tokens={res_base['tokens']}, chi_eff={res_base['mps'].get('chi_eff_mean')}, IPR={res_base['mps'].get('ipr_mean')}, v_mot={res_base['motor'].get('motor_velocity_mean')}")

        # 2. Erika LoRA (LoRA ON)
        set_adapter("on")
        time.sleep(0.5)
        res_erika = query_model(prompt, "12b_erika")
        res_erika["prompt_id"] = pid
        results["erika"].append(res_erika)
        print(f"  [ERIKA] tokens={res_erika['tokens']}, chi_eff={res_erika['mps'].get('chi_eff_mean')}, IPR={res_erika['mps'].get('ipr_mean')}, v_mot={res_erika['motor'].get('motor_velocity_mean')}")

    # Retorna ao modo padrão (OFF)
    set_adapter("off")

    # Síntese Estatística
    def agg(data_list, path):
        vals = []
        for d in data_list:
            curr = d
            for p in path:
                if isinstance(curr, dict):
                    curr = curr.get(p)
                else:
                    curr = None
            if curr is not None and isinstance(curr, (int, float)):
                vals.append(curr)
        return round(statistics.mean(vals), 4) if vals else 0.0

    summary = {
        "base": {
            "chi_eff_mean": agg(results["base"], ["mps", "chi_eff_mean"]),
            "ipr_mean": agg(results["base"], ["mps", "ipr_mean"]),
            "pr_traj_mean": agg(results["base"], ["mps", "pr_traj"]),
            "svd_entropy_mean": agg(results["base"], ["mps", "svd_entropy_mean"]),
            "motor_velocity_mean": agg(results["base"], ["motor", "motor_velocity_mean"]),
            "motor_cosine_drift": agg(results["base"], ["motor", "motor_cosine_drift"]),
            "unique_ratio": agg(results["base"], ["motor", "unique_ratio"]),
            "attention_entropy_last": agg(results["base"], ["attention_entropy_last"]),
        },
        "erika": {
            "chi_eff_mean": agg(results["erika"], ["mps", "chi_eff_mean"]),
            "ipr_mean": agg(results["erika"], ["mps", "ipr_mean"]),
            "pr_traj_mean": agg(results["erika"], ["mps", "pr_traj"]),
            "svd_entropy_mean": agg(results["erika"], ["mps", "svd_entropy_mean"]),
            "motor_velocity_mean": agg(results["erika"], ["motor", "motor_velocity_mean"]),
            "motor_cosine_drift": agg(results["erika"], ["motor", "motor_cosine_drift"]),
            "unique_ratio": agg(results["erika"], ["motor", "unique_ratio"]),
            "attention_entropy_last": agg(results["erika"], ["attention_entropy_last"]),
        }
    }

    out_file = "/content/omni_worker/data/comparacao_12b_base_vs_erika_telemetry.json"
    with open(out_file, "w") as f:
        json.dump({"summary": summary, "runs": results}, f, indent=2)

    print("\n=== RESUMO COMPARATIVO (12B BASE vs ERIKA LORA) ===")
    print(json.dumps(summary, indent=2))
    print(f"\nSalvo com sucesso em: {out_file}")

if __name__ == "__main__":
    main()
