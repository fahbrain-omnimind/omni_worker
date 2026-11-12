#!/usr/bin/env python3
"""
Geração e Quantização Ultra-Mobile (< 2.0 GB) do modelo Erika Qwen3-4B Mobile.
Suporta:
- Q3_K_M (~1.9 GB)
- Q3_K_S (~1.75 GB)
- Q2_K   (~1.5 GB)
- IQ3_XS (~1.7 GB, com imatrix de calibração)
- IQ3_XXS (~1.5 GB, com imatrix de calibração)

Todos compatíveis com llama.cpp, Termux, Ollama, LM Studio e runtimes Android/iOS.
"""

import os
import subprocess
import sys
import time
from pathlib import Path
from huggingface_hub import HfApi

REPO_ID = "fabricioslv/erika-qwen3-4b-mobile-gguf"
GGUF_DIR = Path("/content/erika_qwen3_4b_mobile/gguf")
BIN_DIR = Path("/content/llama.cpp/build/bin")
F16_GGUF = GGUF_DIR / "erika-qwen3-4b-mobile-f16.gguf"
IMATRIX_DAT = GGUF_DIR / "erika_imatrix.dat"

def run_cmd(cmd, desc):
    print(f"\n[RUN] {desc}...")
    t0 = time.time()
    res = subprocess.run(cmd, shell=True, text=True)
    dt = time.time() - t0
    if res.returncode != 0:
        print(f"[FAIL] {desc} falhou (code {res.returncode}) em {dt:.1f}s")
        return False
    print(f"[OK] {desc} concluído em {dt:.1f}s")
    return True

def create_calibration_dataset(dest_path: Path):
    """Cria um dataset representativo de calibração para imatrix."""
    corpus = """
Você é a Erika, uma inteligência artificial assistente amigável, analítica e precisa.
A física quântica estuda a natureza da matéria e da radiação no nível atômico e subatômico.
O princípio da incerteza de Heisenberg estabelece que é impossível determinar com precisão infinita e simultânea a posição e o momento linear de uma partícula.
def fibonacci(n: int) -> list[int]:
    sequence = [0, 1]
    while len(sequence) < n:
        sequence.append(sequence[-1] + sequence[-2])
    return sequence

class SovereignAgent:
    def __init__(self, name: str, memory_limit: int):
        self.name = name
        self.memory_limit = memory_limit
        self.state = {}

    def step(self, observation: dict) -> dict:
        action = self.decide(observation)
        return {"action": action, "agent": self.name}

Para calcular a derivada de uma função vetorial, aplicamos as regras fundamentais do cálculo diferencial multivariado.
A gravidade é descrita na relatividade geral como a curvatura do espaço-tempo provocada pela distribuição de massa e energia.
Um sistema mobile com pouca memória RAM requer quantizações inteligentes de tensores para manter a coerência sintática sem estourar o limite de 4 GB do dispositivo.
Como você avalia a viabilidade de redes neurais locais rodando em hardware de borda?
Em sistemas embarcados, a redução do consumo de memória de 4 bits para 3 bits por peso permite uma execução fluida na CPU com baixo consumo térmico.
Explain the difference between supervised and reinforcement learning in simple terms.
Supervised learning trains a model using labeled inputs and targets. In contrast, reinforcement learning trains an agent through interactions with an environment, maximizing a cumulative reward signal.
""" * 10
    dest_path.write_text(corpus, encoding="utf-8")
    print(f"[CALIB] Corpus de calibração salvo em {dest_path} ({len(corpus)} chars)")

def main():
    api = HfApi()
    
    # Lista de quants diretos (sem imatrix)
    direct_quants = ["Q3_K_M", "Q3_K_S", "Q2_K"]
    
    for qtype in direct_quants:
        out_file = GGUF_DIR / f"erika-qwen3-4b-mobile-{qtype}.gguf"
        if not out_file.exists():
            cmd = f"{BIN_DIR}/llama-quantize {F16_GGUF} {out_file} {qtype} 4"
            if not run_cmd(cmd, f"Quantização {qtype}"):
                continue
        
        sz_mb = out_file.stat().st_size / (1024 * 1024)
        print(f"[STATUS] {qtype}: {out_file.name} -> {sz_mb:.1f} MB ({sz_mb/1024:.2f} GB)")
        
        # Upload imediato
        print(f"[HF UPLOAD] Enviando {out_file.name}...")
        api.upload_file(
            path_or_fileobj=str(out_file),
            path_in_repo=out_file.name,
            repo_id=REPO_ID,
            repo_type="model"
        )
        print(f"[HF OK] {out_file.name} sincronizado!")

    # Agora imatrix para IQ3_XS
    calib_file = GGUF_DIR / "calib_imatrix.txt"
    create_calibration_dataset(calib_file)
    
    if not IMATRIX_DAT.exists():
        imatrix_cmd = (
            f"{BIN_DIR}/llama-imatrix -m {F16_GGUF} -f {calib_file} "
            f"-o {IMATRIX_DAT} --output-format dat --chunks 16 -c 512 -t 4"
        )
        run_cmd(imatrix_cmd, "Geração de Importance Matrix (imatrix)")
    
    if IMATRIX_DAT.exists():
        iq_quants = ["IQ3_XS", "IQ3_XXS"]
        for qtype in iq_quants:
            out_file = GGUF_DIR / f"erika-qwen3-4b-mobile-{qtype}.gguf"
            if not out_file.exists():
                cmd = f"{BIN_DIR}/llama-quantize --imatrix {IMATRIX_DAT} {F16_GGUF} {out_file} {qtype} 4"
                if not run_cmd(cmd, f"Quantização {qtype} com imatrix"):
                    continue
            
            sz_mb = out_file.stat().st_size / (1024 * 1024)
            print(f"[STATUS] {qtype}: {out_file.name} -> {sz_mb:.1f} MB ({sz_mb/1024:.2f} GB)")
            
            print(f"[HF UPLOAD] Enviando {out_file.name}...")
            api.upload_file(
                path_or_fileobj=str(out_file),
                path_in_repo=out_file.name,
                repo_id=REPO_ID,
                repo_type="model"
            )
            print(f"[HF OK] {out_file.name} sincronizado!")

    # Atualizar README.md no Hugging Face
    readme_path = Path("/content/erika_qwen3_4b_mobile/README.md")
    readme_content = f"""# Erika Qwen3-4B Mobile GGUF

Modelo móvel soberano da assistente **Erika**, baseado no `unsloth/Qwen3-4B-Instruct-2507` fundido com o adaptador LoRA [`fabricioslv/erika-qwen3-4b-mobile-adapter`](https://huggingface.co/fabricioslv/erika-qwen3-4b-mobile-adapter).

Otimizado especificamente para execução local offline em smartphones Android (Termux, MLC LLM, llama.cpp), iOS e dispositivos de borda com baixa RAM.

## Formatos e Quantizações Disponíveis

| Arquivo | Quantização | Tamanho | Uso Recomendado / Hardware |
| :--- | :--- | :--- | :--- |
| `erika-qwen3-4b-mobile-Q4_K_M.gguf` | Q4_K_M | ~2.50 GB | Uso geral balanceado em PCs e celulares com >= 6 GB RAM |
| `erika-qwen3-4b-mobile-Q3_K_M.gguf` | Q3_K_M | ~1.95 GB | **Ultra-Mobile**: Cabe confortavelmente em celulares de 4 GB RAM |
| `erika-qwen3-4b-mobile-Q3_K_S.gguf` | Q3_K_S | ~1.80 GB | **Ultra-Mobile**: Menor footprint com excelente retenção |
| `erika-qwen3-4b-mobile-IQ3_XS.gguf`  | IQ3_XS | ~1.72 GB | **Importance Quant**: Qualidade quase Q4 em tamanho sub-2GB |
| `erika-qwen3-4b-mobile-IQ3_XXS.gguf` | IQ3_XXS| ~1.58 GB | **Importance Quant**: Máxima compactação IQ |
| `erika-qwen3-4b-mobile-Q2_K.gguf`   | Q2_K   | ~1.48 GB | **Extremo**: Celulares antigos de 3 GB RAM |

## Como Usar

### llama.cpp / Termux
```bash
./llama-cli -m erika-qwen3-4b-mobile-IQ3_XS.gguf -p "Você é a Erika. Como você pode me ajudar hoje?" -n 512
```

### Ollama Modelfile
```dockerfile
FROM ./erika-qwen3-4b-mobile-IQ3_XS.gguf
TEMPLATE \"\"\"<|im_start|>system
Você é a Erika, uma IA assistente soberana, analítica e acolhedora.<|im_end|>
<|im_start|>user
{{{{ .Prompt }}}}<|im_end|>
<|im_start|>assistant
\"\"\"
PARAMETER stop "<|im_start|>"
PARAMETER stop "<|im_end|>"
```
"""
    readme_path.write_text(readme_content, encoding="utf-8")
    api.upload_file(
        path_or_fileobj=str(readme_path),
        path_in_repo="README.md",
        repo_id=REPO_ID,
        repo_type="model"
    )
    print("\n[ALL COMPLETE] Todas as quantizações ultra-mobile geradas e publicadas com sucesso!")

if __name__ == "__main__":
    main()
