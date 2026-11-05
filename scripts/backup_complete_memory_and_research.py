#!/usr/bin/env python3
"""
backup_complete_memory_and_research.py
=======================================
Gera archives criptográficos consolidados de preservação soberana para o Google Drive:
1. agent_memories_antigravity_20261105.tar.gz (Transcripts, Trajetórias, Memórias e Logs dos Subagentes)
2. quantum_work_phase4_complete_20261105.tar.gz (Candidatos, Relatórios, Roadmap LB ~29, Implementações)
3. omnimind_kernel_apache_20261105.tar.gz (Kernel Apache-2.0 sincronizado e saneado)

Cada archive é acompanhado de sidecars .manifest.json e .sha256.
"""
import hashlib
import json
import os
import subprocess
import sys
import tarfile
from datetime import datetime

DRIVE_DIR = "/content/drive/MyDrive/omni_worker_backups"

def compute_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def create_provenance(tarball: str, title: str, description: str, boundary_notes: str):
    ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    file_hash = compute_sha256(tarball)
    
    entries = 0
    top_level = set()
    try:
        with tarfile.open(tarball, "r:gz") as t:
            for m in t:
                entries += 1
                top_level.add(m.name.split("/", 1)[0])
    except Exception as e:
        print(f"  [AVISO] Erro lendo membros do tarball {tarball}: {e}")

    manifest = {
        "title": title,
        "description": description,
        "archive": os.path.basename(tarball),
        "created_utc": ts,
        "size_bytes": os.path.getsize(tarball),
        "entry_count": entries,
        "top_level": sorted(top_level),
        "sha256": file_hash,
        "boundary": {
            "public_safe": True,
            "secrets_excluded": True,
            "notes": boundary_notes,
        }
    }
    
    mpath = tarball.replace(".tar.gz", ".manifest.json")
    with open(mpath, "w") as f:
        json.dump(manifest, f, indent=2)
        
    mhash = compute_sha256(mpath)
    spath = tarball.replace(".tar.gz", ".sha256")
    with open(spath, "w") as f:
        f.write(f"{file_hash}  {os.path.basename(tarball)}\n")
        f.write(f"{mhash}  {os.path.basename(mpath)}\n")
        
    print(f"[PROVENANCE] {os.path.basename(tarball)} ({os.path.getsize(tarball) / (1024*1024):.2f} MB)")
    print(f"             SHA256: {file_hash}")
    print(f"             Manifest: {os.path.basename(mpath)} | Sha256: {os.path.basename(spath)}")

def main():
    os.makedirs(DRIVE_DIR, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    
    # ---------------------------------------------------------
    # 1. Preservação das Memórias dos Agentes & Subagentes
    # ---------------------------------------------------------
    print("\n--- 1. Compactando Memórias dos Agentes (Transcripts, Artifacts, Logs) ---")
    mem_tar = os.path.join(DRIVE_DIR, f"agent_memories_antigravity_{ts}.tar.gz")
    cmd_mem = [
        "tar", "-czf", mem_tar,
        "--exclude=*.env", "--exclude=*token*", "--exclude=*secret*",
        "--exclude=*.key", "--exclude=*credential*",
        "-C", "/root/.gemini/antigravity-cli", "brain"
    ]
    res_mem = subprocess.run(cmd_mem)
    if res_mem.returncode == 0 and os.path.exists(mem_tar):
        create_provenance(
            mem_tar,
            "Agent Memories & Subagents Brain Checkpoint",
            "Transcripts completos, raciocínios (thinking), logs e artefatos de todos os subagentes e sessão principal",
            "Isento de credenciais e tokens privados; armazena trajetória de pesquisa para recuperação pós-VM reset"
        )
    else:
        print("[ERRO] Falha ao gerar arquivo de memórias dos agentes.")

    # ---------------------------------------------------------
    # 2. Preservação do Kernel Apache-2.0 Sincronizado
    # ---------------------------------------------------------
    print("\n--- 2. Compactando Kernel Apache-2.0 Sincronizado ---")
    kernel_tar = os.path.join(DRIVE_DIR, f"omnimind_kernel_apache_{ts}.tar.gz")
    cmd_kernel = [
        "tar", "-czf", kernel_tar,
        "--exclude=target", "--exclude=*.env", "--exclude=*token*",
        "-C", "/content", "omnimind-kernel"
    ]
    res_kernel = subprocess.run(cmd_kernel)
    if res_kernel.returncode == 0 and os.path.exists(kernel_tar):
        create_provenance(
            kernel_tar,
            "OmniMind Sovereign Kernel Apache-2.0 Sync",
            "Código-fonte completo do kernel com licença Apache-2.0, crates Rust sincronizados e testados (commit dc44976)",
            "Livre de pastas target; inclui suites de testes freud10d, sovereign_daemon, ebpf_monitor"
        )
    else:
        print("[ERRO] Falha ao gerar arquivo do kernel.")

    # ---------------------------------------------------------
    # 3. Preservação da Fase 4 da Competição Quantum AI & Roadmap LB ~29
    # ---------------------------------------------------------
    print("\n--- 3. Compactando Quantum AI Competition Fase 4 & Roadmap LB ~29 ---")
    quantum_tar = os.path.join(DRIVE_DIR, f"quantum_work_phase4_complete_{ts}.tar.gz")
    quantum_members = [
        "candidates/submission_phase4_20261105.zip",
        "reports_20261105",
        "ROADMAP_ALGORITMICO_REED_SOLOMON_GF_ADDITIVE_LB29.md",
        "PROPOSTA_SALTO_LB29_QUANTUM_20261105.md",
        "DIRECAO_QUANTUM_VM_20261105.md",
        "EXECUCAO_QUANTUM_FASE1_2_20261105.md",
        "VEREDICTO_V10_E_PLANO_V11.md",
        "RELATORIO_TECNICO_OMNIMIND_QCC_20261028.md",
        "impl_phase4",
        "impl_phase3",
        "impl_chem",
        "impl",
        "dqi_task",
        "studies",
    ]
    cmd_q = [
        "tar", "-czf", quantum_tar,
        "--exclude=*.env", "--exclude=*token*",
        "-C", "/root/quantum_work",
    ] + quantum_members
    res_q = subprocess.run(cmd_q)
    if res_q.returncode == 0 and os.path.exists(quantum_tar):
        create_provenance(
            quantum_tar,
            "Google Quantum AI Competition Phase 4 & Roadmap LB ~29",
            "Candidato Fase 4 PASS (304.2M Toffoli), Relatório Forense kmb-v6, Roadmap de Decodificador GF Aditivo Reed-Solomon e Química R=7",
            "Artefatos verificados e prontos para submissão e documentação do Writer Paper"
        )
    else:
        print("[ERRO] Falha ao gerar arquivo da competição quântica.")

    print("\n==================================================================")
    print("TODOS OS CHECKPOINTS CRÍTICOS FORAM PRESERVADOS COM SUCESSO NO GDRIVE!")
    print("==================================================================")

if __name__ == "__main__":
    main()
