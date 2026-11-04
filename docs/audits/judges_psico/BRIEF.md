# BRIEF — Auditoria cooperativa de dados (juízes CLI)

Dataset: `/content/omni_worker/data/psicodiagnostico_v/` (cópia local de HF `fabricioslv/psicodiagnostico-v-embodied-results`, READ-ONLY; não editar nem apagar nada ali).
Repo de trabalho: `/content/omni_worker` (escreva SOMENTE o seu documento em `docs/audits/judges_psico/`; NÃO edite `src/`).

## Natureza
Não é competição: é auditoria dos DADOS. Cada juiz cobre uma fatia com minúcia, escreve o próprio documento; depois cada um lê os dos outros e concorda / refuta / incrementa (rodada 2). Discordar com evidência é desejável; concordar quando o colega está certo também.

## Regras (AGENTS.md — REGRA ZERO e INTEGRIDADE)
- Nada de dado inventado/simulado. Toda afirmação numérica deve vir de uma consulta/arquivo que VOCÊ executou; cite o comando/consulta e o caminho.
- Tags: [DADO] (medido, com fonte) · [DERIVADO] (calculado de dados) · [INTERPRETAÇÃO] · [LIMITE]. Se não sabe: NÃO SEI. Se não encontrou: NÃO LOCALIZADO.
- `thinking_trace` / raciocínio vazado são ARTEFATO RICO de análise (leitura psicanalítica associativa, camadas internas), não defeito: descreva-os, quantifique-os e proponha como usá-los.
- Segredos: nunca imprimir tokens/chaves; reporte se achar algum.
- Contexto de verdade: a monografia `MONOGRAFIA_ESTUDO_PSICODIAGNOSTICO_V.md` e `AUDITORIA_GEMMA4_BATERIA_TOTAL_20261103.md` (32 itens) são alegações a verificar, não verdades.

## Fatias
- **A — agent (Cursor)**: `embodied_psychodiagnostic_bank.sqlite` inteiro (models, benchmark_runs 389, module_scores, quati/mmpi_profiles, evaluation_provenance, mps_bateria_records, quota_schedule_queue, thinking_trace_metrics) vs. contagens e alegações da monografia; sha256/proveniência; consistência entre tabelas; colunas NULL/0/vazias.
- **B — kilo**: V10/V11: `v10_colab_benchmark.sqlite` (v10_runs, v10_scene_scores, rorschach_b_runs, cognitive_runs), `gemma4_runs_20261030/*.parquet`, `cenas_v10_refinadas.py`, `psicodiagnostico_*.json/parquet`, `v10_v11_runs/`, `10turn_*`, `peer_cross_evals/`, `protocols/`, scripts em `scripts/`: consistência json↔parquet↔sqlite, scorer heurístico, pranchas Rorschach (amostrar respostas, achar degeneração/repetição/vazamento).
- **C — hermes**: `gemma4_runs_20261030/judges/` (AGGREGATE_ABC, ANALYSIS_CONSOLIDATED, leaked_reasoning_gemma4, MANIFEST_SHA256 — verificar os hashes DE FATO), `judges/CONSENSUS_*.json`, `erika_mps_5turnos/`, `activity_db/*.sqlite`, `README.md` do dataset; acordo inter-juízes (recalcule quando possível), vieses, e a leitura do raciocínio vazado como material psicanalítico.

## Entrega rodada 1
Arquivo `docs/audits/judges_psico/<JUIZ>_R1_<fatia>.md` com: método (comandos), achados tagueados, tabela de alegações verificadas (VERIFICADO/DIVERGENTE/NÃO LOCALIZADO), lacunas, e perguntas para os outros juízes.
