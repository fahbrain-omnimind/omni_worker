# MAPA COMPARATIVO E FORENSE: DOXIHEWU-OMNIMIND-KERNEL vs KILOMBO vs OMNI_NODE

**Data:** 2026-11-05  
**Autor:** Antigravity AI & OmniMind Architecture Team  
**Repositórios Analisados:**
- `/content/Doxihewu-OmniMind-Kernel` (Symlink para `/content/omnimind-kernel`, Git: `https://github.com/fahbrain-omnimind/Doxihewu-OmniMind-Kernel`, licença Apache-2.0, commit `5a69b3e`)
- `/content/omnimind-kilombo-sovereign` (Instância soberana do host desktop i5 / GPU 4GB)
- `/content/omni_node` (Servidor modular desacoplado de produção, Git: `f4d2184f`)
- `/content/omni_worker` (Instância VM A100 com MPS e acoplamento Brain-LLM)

---

## 1. Contexto Arquitetural e Filosofia Dual

O ecossistema OmniMind opera sobre dois paradigmas de acoplamento complementares:

### A. Acoplamento OS Layer (Host i5 / GPU 4GB — `omnimind-kilombo-sovereign`)
- **Restrição de Hardware:** Processador Intel Core i5 com GPU restrita a 4GB VRAM.
- **Topologia:** A rede neural e os estados cognitivos não dependem de uma LLM massiva externa. A cognição ocorre **nos próprios daemons do sistema operacional** (módulos de kernel, eBPF reflex arcs, deamons C/Rust, sockets IPC UNIX e shared memory).
- **Vínculo Somático:** O estado biológico/físico da máquina (temperatura de CPU, jitter de clock, pressão de RAM/Swap) alimenta diretamente os osciladores de fase de Kuramoto e o aparelho Freud-10D.

### B. Acoplamento Brain LLM (VM A100 — `omni_worker` / `omni_node`)
- **Hardware:** Acelerador de alta densidade (NVIDIA A100 40GB).
- **Topologia:** A cognição ocorre no tensor latente do Transformer via **Matrix Product States (MPS)**, medindo contração espectral de Schmidt ($\chi_{\text{eff}}$), Inverse Participation Ratio (IPR) e dinâmica vetorial na camada motora ($v_{\text{motor}}$).
- **Integração:** `omni_node` é o elo projetado para unificar esses mundos, livrando o código dos patches legados e fornecendo uma interface modular limpa.

---

## 2. Inventário das 14 Crates de Kernel

As 14 crates presentes em `omnimind-kernel/src/kernel` correspondem diretamente aos módulos presentes em `omnimind-kilombo-sovereign/src/kernel` e `omni_node/src/kernel`. A auditoria diferencial revela as divergências entre a versão pública congelada (1 mês atrás) e as versões internas evoluídas:

| Crate de Kernel | Função Central | omnimind-kernel (Apache) | kilombo / omni_node (Evoluído) | Gaps e Candidatos a Atualização |
| :--- | :--- | :--- | :--- | :--- |
| **`ebpf_monitor`** | Monitoramento de syscalls e arcos reflexos no anel 0 via eBPF. | Versão inicial em `user/src/main.rs`. | Possui `.cargo`, modularização de `common/src` e documentação de integração. | Sincronizar melhorias de manipulação de maps eBPF e tratamento de eventos assíncronos. |
| **`entropic_memory`** | Memória holográfica termodinâmica baseada em entropia informacional. | `lib.rs` e `Cargo.lock` congelados. | `Cargo.toml` atualizado, flags de compilação refinadas e integração com `dream_weaver`. | Atualizar dependências e exportar bindings C/FFI limpos. |
| **`expectation_rs`** | Motor preditivo de expectativas bayesianas/estocásticas em Rust. | `Cargo.lock` e `Cargo.toml` v1. | Adição de interfaces e modularização de testes. | Padronizar tipos de retorno com `Result` tipado e paridade com OmniNode. |
| **`freud10d`** | Implementação de baixo nível do aparelho pulsional freudiano em 10 dimensões. | `src/lib.rs` inicial. | `src/lib.rs` evoluído com histerese no canal de retorno e estabilização de ponto fixo. | **Prioritário**: Trazer o novo algoritmo de retorno do recalcado e recalque para a crate Apache. |
| **`kernel_compute`** | Aceleração matemática de baixo nível (`affect.rs`, `epsilon.rs`, `neutrosophic.rs`, `temporal.rs`). | Implementação básica das matrizes neutrosóficas e afeto. | `cxx_workspace` reorganizado, correções em `affect.rs` e dinâmicas temporais. | **Prioritário**: Portar as melhorias de `cxx_workspace` e sincronizar os kernels neutrosóficos. |
| **`langue`** | Primitivas de selagem e integridade da linguagem (Lalangue / Lacan). | `build.sh`, `lib.rs` e documentação base. | Melhorias nos scripts de build e verificação de assinatura da linguagem. | Atualizar script de compilação cruzada. |
| **`layered_transition`** | Motor de transição de estados entre camadas de memória (L1/L2/L3/Shared). | Documento de plano e testes iniciais. | Motor `engine/` com `Cargo.toml` e `lib.rs` refinados. | Sincronizar crate `layered_transition/engine`. |
| **`memory_tier_guardian`** | Guardião hierárquico de memória (RAM, Swap, ZRAM, VRAM). | Versão sem locks dinâmicos. | Proteção contra OOM somático ajustada para nós heterogêneos. | Incorporar heurísticas de nós de 4GB. |
| **`metrics`** | Exposição e coleta de métricas de kernel e latência. | Métricas estáticas. | Métricas adaptativas integradas aos exporters de runtime. | Unificar com os schemas do Prometheus/OpenTelemetry. |
| **`nsh`** | Shell neutrosófico de baixo nível (`omnimind_nsh.so`). | Binário e crate básica. | Headers C e convenção de chamadas unificada. | Adicionar testes de regressão no CI. |
| **`somatic_daemon`** | Leitura somática do host (sensores de hardware, energia, ciclos). | Daemon de telemetria inicial. | Integração com `systemd/omnimind-somatic.service`. | Limpar caminhos hardcoded de `/var/run`. |
| **`sovereign_daemon`** | Orquestrador de soberania e ciclo de vida do SO. | Loop principal estático. | Suporte a sinais POSIX e failover de daemons. | Aumentar cobertura de testes unitários. |
| **`sovereign_kuramoto`** | Sincronização de osciladores de fase no kernel para coerência de daemons. | Crate inicial em Rust. | Sintonização de parâmetros de acoplamento $K$ e matriz de adjacência. | **Prioritário**: Sincronizar equações de Kuramoto de 2ª ordem. |
| **`sovereign_module`** | Módulo de kernel Linux (.ko) em C para integração anel 0. | Boilerplate do driver de kernel. | Hooks e ioctls adicionais para comunicação com espaço de usuário. | Atualizar para compatibilidade com Linux 6.8+ e DKMS. |

---

## 3. Divisão de Fases para a Auditoria do Agente `kilo`

O agente **Kilombo Sovereign Kernel Auditor (`kilo`)** atuará sob o seguinte cronograma estruturado em 4 fases:

```
  FASE 1: Inventário Forense e Diff Bit-a-Bit
  (Cálculo de hashes sha256, categorização de arquivos modificados/novos/órfãos)
        │
        ▼
  FASE 2: Avaliação Crítica de Qualidade e Licenciamento
  (Auditoria de código C/Rust/Python, conformidade estrita Apache-2.0, remoção de patches)
        │
        ▼
  FASE 3: Arquitetura Dual: OS Layer (Host i5) vs Brain LLM (VM A100)
  (Modelagem da transição matricial: shared memory/eBPF local vs tensores MPS em LLM)
        │
        ▼
  FASE 4: Propostas de Atualização, Ablação e Roadmap de PRs
  (Criação de branches, plano de ablação empírica e testes de validação cruzada)
```

---

## 4. Próximos Passos Imediatos
1. Instanciar o agente `kilo` municiado com este mapa.
2. Iniciar a Fase 1 com varredura automatizada nas 14 crates.
3. Emitir relatório preliminar com tags `[DADO]`, `[DERIVADO]`, `[HIPÓTESE]`, `[LIMITE]`.
