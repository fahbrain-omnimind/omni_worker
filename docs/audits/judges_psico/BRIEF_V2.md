# BRIEF V2 — Auditoria Técnica do Acervo Expandido (HF commit a67b3b4e)

Local do Acervo: `/content/omni_worker/data/psicodiagnostico_v_v2/` (READ-ONLY).
Repo: `/content/omni_worker/` (Edições permitidas SOMENTE em `docs/audits/judges_psico/`).

## Fatos Verificados pela Apuração Preliminar:
1. **Manifesto SHA256 Reconciliado nos Juízes**:
   - `judge_scores`: 32/32 matches exatos (100%).
   - `judge_parts`: 80/80 matches exatos (100%).
   - `bundles_respostas_cruas`: 20/20 matches exatos (100%).
   Total de 136 hashes verificados com precisão. O gap anterior de ausência de scores brutos foi RESOLVIDO.
2. **Novos Dados Disponíveis**:
   - `data_sanitized/` completo com `runs_by_phase/` (v8, v9, v10, unified), `kaggle_v11_v{2,3,4}/` com 1.846+ vereditos e `thinking_traces/`.
   - `judges/` com scores e bundles de wave1, wave2, rep_n2, colab, triade.

## Diretrizes de Execução dos Agentes CLI:
- **Orquestração e Subagentes**: Decomponha sua análise criando e coordenando subagentes para lotes específicos ou executando passos refinados e iterativos.
- Não gere dados simulados. Todo número deve vir de consulta executada no disco.
- O thinking_trace é material rico para interpretação psicanalítica das camadas e raciocínio interno.

## Entregas:
- **KILO (Fatia B expandida)**: `docs/audits/judges_psico/KILO_EXPANDED_AUDIT.md` (Cruzar runs_by_phase, thinking_traces e v11_runs).
- **HERMES (Fatia C expandida)**: `docs/audits/judges_psico/HERMES_EXPANDED_AUDIT.md` (Cruzar scores brutos recém-chegados com os 7 consensos e avaliar agreement real).
