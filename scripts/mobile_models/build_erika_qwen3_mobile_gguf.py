#!/usr/bin/env python3
"""Pipeline de Merge LoRA e Quantização Mobile (GGUF Q4_K_M) para Erika Qwen3-4B.
===================================================================================

1. Baixa o adaptador LoRA de `fabricioslv/erika-qwen3-4b-mobile-adapter`.
2. Baixa o modelo base 16-bit correspondente (`unsloth/Qwen3-4B-Instruct-2507` ou `Qwen/Qwen3-4B-Instruct-2507`).
3. Executa o merge limpo dos pesos (merge_and_unload) em bfloat16.
4. Converte para GGUF via llama.cpp (convert_hf_to_gguf.py).
5. Quantiza para formato mobile otimizado (Q4_K_M para Android/Termux/Ollama/llama.cpp).
6. Faz upload dos GGUFs para o Hugging Face.

Autor: Sujeito-Processo OmniMind & Fabrício da Silva
Data: 2026-11-12
Regra de Integridade: AGENTS.md (100% Empírico na VM).
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

# Monkey-patch para contornar incompatibilidade de versão do torchao no peft
try:
    import peft.import_utils
    import peft.tuners.lora.torchao
    peft.import_utils.is_torchao_available = lambda: False
    peft.tuners.lora.torchao.is_torchao_available = lambda: False
except Exception:  # noqa: BLE001, S110
    pass

import torch
from huggingface_hub import HfApi, snapshot_download
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

ADAPTER_REPO = "fabricioslv/erika-qwen3-4b-mobile-adapter"
DEFAULT_BASE_MODEL = "unsloth/Qwen3-4B-Instruct-2507"
OUTPUT_DIR = Path("/content/erika_qwen3_4b_mobile")
LLAMA_CPP_DIR = Path("/content/llama.cpp")


def download_adapter(adapter_repo: str, target_dir: Path) -> Path:
    print(f"\n[1/6] Baixando adapter LoRA de {adapter_repo}...")
    t0 = time.time()
    dest = target_dir / "adapter"
    dest.mkdir(parents=True, exist_ok=True)
    snapshot_download(repo_id=adapter_repo, local_dir=str(dest))
    print(f"[OK] Adapter baixado em {time.time() - t0:.1f}s -> {dest}")
    return dest


def download_and_merge(base_model_name: str, adapter_dir: Path, merged_out_dir: Path) -> Path:
    print(f"\n[2/6] Carregando modelo base: {base_model_name}...")
    t0 = time.time()

    device = "cpu"
    dtype = torch.bfloat16
    print(f"Carregando em {device} com {dtype}...")

    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        torch_dtype=dtype,
        device_map=device,
        trust_remote_code=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(str(adapter_dir), trust_remote_code=True)
    print(f"[OK] Modelo base carregado em {time.time() - t0:.1f}s")

    print("\n[3/6] Aplicando LoRA adapter e executando merge_and_unload...")
    t1 = time.time()
    model = PeftModel.from_pretrained(base_model, str(adapter_dir))
    merged_model = model.merge_and_unload()
    print(f"[OK] Merge concluído em {time.time() - t1:.1f}s")

    print(f"\n[4/6] Salvando modelo merged em {merged_out_dir}...")
    merged_out_dir.mkdir(parents=True, exist_ok=True)
    merged_model.save_pretrained(str(merged_out_dir), safe_serialization=True)
    tokenizer.save_pretrained(str(merged_out_dir))
    print("[OK] Modelo merged salvo com sucesso!")
    return merged_out_dir


def convert_and_quantize(merged_dir: Path, quant_bin: Path, gguf_out_dir: Path) -> dict[str, Path]:
    print("\n[5/6] Convertendo para GGUF e quantizando para formato mobile...")
    gguf_out_dir.mkdir(parents=True, exist_ok=True)
    f16_gguf = gguf_out_dir / "erika-qwen3-4b-mobile-f16.gguf"
    q4_gguf = gguf_out_dir / "erika-qwen3-4b-mobile-Q4_K_M.gguf"

    # Conversão HF -> GGUF f16
    convert_script = LLAMA_CPP_DIR / "convert_hf_to_gguf.py"
    if not f16_gguf.exists():
        print("Executando convert_hf_to_gguf.py...")
        subprocess.run([
            sys.executable, str(convert_script),
            str(merged_dir),
            "--outfile", str(f16_gguf),
            "--outtype", "f16"
        ], check=True)
        print(f"[OK] GGUF f16 gerado: {f16_gguf} ({f16_gguf.stat().st_size / 1e9:.2f} GB)")

    # Quantização para Q4_K_M (Padrão Mobile)
    if not q4_gguf.exists():
        print("Quantizando para Q4_K_M via llama-quantize...")
        subprocess.run([
            str(quant_bin),
            str(f16_gguf),
            str(q4_gguf),
            "Q4_K_M"
        ], check=True)
        print(f"[OK] GGUF Mobile Q4_K_M gerado: {q4_gguf} ({q4_gguf.stat().st_size / 1e9:.2f} GB)")

    return {"f16": f16_gguf, "q4_k_m": q4_gguf}


def upload_to_hf(files: dict[str, Path], target_repo: str) -> None:
    api = HfApi()
    print(f"\n[6/6] Criando/atualizando repositório {target_repo}...")
    api.create_repo(repo_id=target_repo, repo_type="model", exist_ok=True)
    for tag, fpath in files.items():
        if tag == "f16":
            # O f16 é gigante (8GB), para mobile o prioritário de upload é o Q4_K_M
            continue
        print(f"Fazendo upload de {fpath.name} ({fpath.stat().st_size / 1e9:.2f} GB)...")
        api.upload_file(
            path_or_fileobj=str(fpath),
            path_in_repo=fpath.name,
            repo_id=target_repo,
            repo_type="model",
            commit_message=f"feat: add {tag.upper()} mobile quantized GGUF model",
        )
        print(f"[OK] {fpath.name} sincronizado no Hugging Face!")


def main():
    parser = argparse.ArgumentParser(description="Build mobile quantized GGUF model from LoRA adapter")
    parser.add_argument("--adapter-repo", default=ADAPTER_REPO, help="Repositório HF do adapter")
    parser.add_argument("--base-model", default=DEFAULT_BASE_MODEL, help="Repositório HF do base model 16-bit")
    parser.add_argument("--upload-repo", default="fabricioslv/erika-qwen3-4b-mobile-gguf", help="Repositório HF para upload do GGUF")
    parser.add_argument("--no-upload", action="store_true", help="Não fazer upload para o HF")
    args = parser.parse_args()

    print("=" * 78)
    print("PIPELINE DE GERAÇÃO DE MODELO MOBILE QUANTIZADO (GGUF)")
    print(f"Adapter: {args.adapter_repo}")
    print(f"Base Model: {args.base_model}")
    print("=" * 78)

    quant_bin = LLAMA_CPP_DIR / "build" / "bin" / "llama-quantize"
    if not quant_bin.exists():
        raise FileNotFoundError(f"Binário llama-quantize não encontrado em {quant_bin}")

    adapter_dir = download_adapter(args.adapter_repo, OUTPUT_DIR)
    merged_dir = OUTPUT_DIR / "merged_hf"
    download_and_merge(args.base_model, adapter_dir, merged_dir)
    gguf_files = convert_and_quantize(merged_dir, quant_bin, OUTPUT_DIR / "gguf")

    if not args.no_upload and args.upload_repo:
        upload_to_hf(gguf_files, args.upload_repo)

    print("\n" + "=" * 78)
    print("[SUCESSO TOTAL] Modelo mobile quantizado gerado e pronto!")
    for tag, p in gguf_files.items():
        print(f"  - {tag.upper()}: {p} ({p.stat().st_size / 1e9:.2f} GB)")
    print("=" * 78)


if __name__ == "__main__":
    main()
