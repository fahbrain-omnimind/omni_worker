# OW-STU-014 — Auditoria do corpus documental soberano

Origem dos dados: /content/omnimind-kilombo-sovereign (read-only). Todos os
números abaixo foram obtidos por comando executado em 2026-11-03; origem
declarada por item. Nenhum arquivo foi modificado.

## 1. Método (comandos)

- Estrutura: `find docs -type d`, `find . -iname '*manifest*'`.
- Links relativos em .md: python regex `\[[^\]]*\]\(([^)]+)\)`, resolução
  contra diretório do arquivo, verificação `os.path.exists`. (3686 links)
- MD5: `find docs -type f -size -50M (md,json,py,txt,yaml,yml) -print0 | xargs -0 md5sum`,
  agrupamento por hash. (10950 arquivos elegíveis)
- Pendências: `grep -riE "TODO|WIP|pendente|draft|rascunho" docs/` (linhas)
  e `grep -rliE ...` (arquivos).

## 2. Manifest gaps (links relativos quebrados)

- Links relativos verificados: 3686
- Alvos distintos inexistentes: 1933
- Causas observadas: caminhos absolutos `/home/fahbrain/...` (não existem
  neste host), arquivos movidos para `archive/`, pastas renomeadas.

Principais alvos ausentes (contagem de referências):

| # | referências | alvo ausente |
|---|---|---|
| 1 | 12 | docs/file:/home/fahbrain/projects/omnimind/src/agents/react_agent.py |
| 2 | 10 | /home/fahbrain/projects/omnimind/scripts/sovereign/sovereign_daemon.py |
| 3 | 10 | /home/fahbrain/projects/omnimind/Paper_v3.1_PT.md |
| 4 | 10 | /home/fahbrain/projects/omnimind/docs/papers/v3/OMNIMIND_PSICANALISE_DA_MECANICA_AO_SUJEITO_PROCESSO_20260517.md |
| 5 | 10 | docs/docs_profissionais/reference/ANALISE_CHECKLIST_7_PERGUNTAS_PSICOANALITICA.md |
| 6 | 10 | docs/reference/ANALISE_CHECKLIST_7_PERGUNTAS_PSICOANALITICA.md |
| 7 | 9 | docs/archive/sessions_2025/docs/CHAOS_ENGINEERING_RESILIENCE.md |
| 8 | 9 | docs/papers/v3/scripts/analysis/desktop_guest_failover_status.py |
| 9 | 9 | docs/papers/v3/src/security/sovereign_glial_daemon.py |
| 10 | 9 | docs/arquivo_obsoleto/archive/sessions_2025/docs/CHAOS_ENGINEERING_RESILIENCE.md |

Arquivos presentes sem referência: NÃO LOCALIZADO (não foi feito inverso
completo por escala; candidato a follow-up).

## 3. Duplicate MD5s

- Arquivos elegíveis (<50MB, extensões textuais) em docs/: 10950
- Hashes duplicados (grupos com >1 arquivo): 774
- Arquivos envolvidos: 2075

Top grupos por número de cópias:

| # | cópias | exemplo de arquivo |
|---|---|---|
| 1 | 476 | docs/DESCOBERTA_CRITICA_AUDIO_SENSORY_2026-01-02.md |
| 2 | 8 | docs/zenodo_packs/.../zenodo_metadata_...json |
| 3 | 4 | docs/zenodo_packs/.../ZENODO_DESCRIPTION_...md |
| 4 | 4 | docs/analysis/diagnostics/APURACAO_FORENSE_COMPLETA.md |
| 5 | 4 | docs/papers/v3/MANIFEST_ZENODO_RELEASE_V45_V46.json |
| 6 | 4 | docs/analysis/performance/ANALISE_LOGS_POS_CORRECAO.md |
| 7 | 4 | docs/analysis/diagnostics/INVESTIGACAO_PSI_BAIXO.md |
| 8 | 4 | docs/papers/v3/SPH_SUJEITO_PROCESSO_HISTORICO_..._EN.md |
| 9 | 4 | docs/analysis/500_cycles_validation/phi_500_cycles_scientific_validation_...json |
| 10 | 3 | docs/papers/v3/OMNIMIND_PRIORIDADE_RESONANCIAS_EXTERNAS_20260529.md |

## 4. Pending docs (TODO/WIP/pendente/draft/rascunho)

- Ocorrências (linhas): 13900
- Arquivos distintos com marcador: 2100

## 5. Top-10 anomalias priorizadas (para relatório ao Artífice)

1. 476 cópias idênticas de DESCOBERTA_CRITICA_AUDIO_SENSORY_2026-01-02.md (MD5 duplicado massivo).
2. 1933 alvos distintos de links markdown inexistentes (manifest gaps).
3. Caminhos absolutos /home/fahbrain/... referenciados em 10+ docs (ambiente morto).
4. 2100 arquivos com marcadores TODO/WIP/pendente/draft/rascunho.
5. Arquivos movidos para archive/ mas links antigos não atualizados (CHAOS_ENGINEERING_RESILIENCE).
6. 774 grupos de hash duplicado (2075 arquivos).
7. Arquivos duplicados em docs/reference vs docs/docs_profissionais/reference.
8. Manifests JSON presentes em docs/reports_runtime sem par correspondente .md (ou vice-versa) — NÃO LOCALIZADO contagem exata; sugerir follow-up.
9. Ausência de data/manifest* no soberano (nenhum encontrado).
10. Arquivos presentes sem referência (inverso) não computado — NÃO LOCALIZADO.

## Nota de integridade
Contagens derivadas de comandos acima. Itens marcados NÃO LOCALIZADO não
foram verificados. Nenhum dado simulado.
## Nota de escopo (Devin, 2026-11-03)

Os alvos quebrados com caminho `/home/fahbrain/...` são links INTERNOS da
documentação soberana apontando para o filesystem do host onde o projeto
vive — não são referências do worker. Verificado: nenhum arquivo em
`omni_worker/src|scripts|docs` depende de `/home/fahbrain` (as únicas
ocorrências locais são o org do GitHub e este relatório). O soberano é
material de referência read-only: os caminhos são válidos no host real;
a fragilidade só aparece em cópias. O achado pertence à higiene do
próprio repo soberano (relativo-vs-absoluto), não a este worker.
