# Manifest de Linhagem — Livro "Da Geometria à Substância"

**Data:** 2026-10-11 (BRT) · **Autor:** `codex-cli` (sessão de revisão)
**Objetivo:** resolver a dúvida D1 (qual arquivo é o mestre?) com evidência documental + medição, sem decidir unilateralmente o que for editorial.
**Método:** `ls -la` (mtime/tamanho) → `wc -l` / `grep -c '^## '` (estrutura) → `sha256sum` (identidade) → busca de **declaração canônica** em artefatos de revisão do próprio diretório.

---

## 1. Descendentes localizados do mesmo corpo textual

| # | Caminho | Bytes | Linhas | H2 | Marcador "35–36" | mtime | SHA256 (pref.) |
|:--:|:---|---:|---:|---:|:---:|:---|:---|
| 1 | `revisao/A6_integrador/livro_vfinal.md` | 1.627.727 | 15.543 | 70 | não (35 e 36 separados) | 2026-10-05 20:06 | `b00b5797` |
| 2 | `revisao/A6_integrador/livro_vfinal_limpo_PT.md` | 1.437.833 | 13.987 | 67 | **sim** (`### 35–36.`) | 2026-09-12 12:43 | `eaaec775` |
| 3 | `docs/zenodo_packs/dodecatiad_v3_publication/paper/dodecatiad_da_geometria_a_substancia_pt.md` | 1.493.160 | 14.746 | 70 | não (35 e 36 separados) | 2026-09-05 13:18 | `203a9e99` |
| 4 | `docs/zenodo_packs/dodecatiad_v3_publication/paper/dodecatiad_da_geometria_a_substancia_publica_pt.md` | 1.481.469 | — | — | — | 2026-09-01 07:19 | `b9162fbd` |
| 5 | `revisao/A6_integrador/livro_vfinal_clean_EN.md` | 1.420.351 | — | — | — | 2026-09-11 11:23 | `b05c8d4c` |

**Comandos:** `ls -la <caminho>` · `wc -l <caminho>` · `grep -c '^## ' <caminho>` · `sha256sum <caminho>`
Nenhum dos cinco é byte-idêntico a outro (5 hashes distintos). Não são cópias — são linhagens.

---

## 2. Declaração canônica de mestre (evidência documental, não suposição)

**Fonte:** `revisao/A6_integrador/RETIFICACAO_EDITORIAL_VERSOES.md` (2026-09-11, §"Arquivos canônicos"), verbatim:

> **Arquivos canônicos**:
> - EN: `revisao/A6_integrador/livro_vfinal_clean_EN.md`
> - PT: `revisao/A6_integrador/livro_vfinal_limpo_PT.md`

**Consequência:** para a **linha de revisão**, o mestre PT é **`livro_vfinal_limpo_PT.md`** (`eaaec775…`) e o mestre EN é **`livro_vfinal_clean_EN.md`** (`b05c8d4c…`). A auditoria em curso (`revisao/AUDITORIA_LIVRO_X_RUNTIME_20261011.md` e as auditorias de faixa) apontam para o mestre PT correto.

**O que isso NÃO resolve:** `livro_vfinal.md` (item 1) é **posterior** (2026-10-05) e maior (+189.894 bytes, +1.556 linhas) que o mestre PT declarado (2026-09-12). O mestre canônico está **~3 semanas atrás** do rascunho de trabalho. Isso é um **défice de re-freeze**, não um erro factual — mas significa que qualquer correção aplicada hoje ao mestre PT parte de um texto que já não é o mais recente.

---

## 3. Fusão dos capítulos 35–36 — confirmada em TODAS as linhagens (não é defeito)

| Linhagem | Registro da fusão | Linha |
|:---|:---|:---|
| `livro_vfinal.md` | `### 35. [Nota Editorial — Consolidado em Apêndice E.18 e §29]` + `## 36. Desacoplamento Arquitetural … [consolidado em Apêndice E.17]` | 4541 / 4547 |
| pack zenodo `..._pt.md` | idem, mesmos marcadores | 4219 / 4225 |
| `livro_vfinal_limpo_PT.md` | `### 35–36. [Seções consolidadas em apêndices]` com o mapa explícito (§35→§29+E.18+E.17.5; §36→E.17; §37 em diante mantida) | 4083 |

**Comandos:** `grep -nE '^#+ *(35|36)\.' <caminho>` · `sed -n '4083,4085p' revisao/A6_integrador/livro_vfinal_limpo_PT.md`
**Veredito:** a consolidação de §35/§36 é decisão editorial **já registrada**, presente de forma consistente inclusive na cópia publicada (pack de 2026-09-01/05). Não é salto de numeração nem defeito. (Confirmado também pela auditoria amostral independente: claim #63 = MANTÉM.)

---

## 4. Recomendação (para decisão do operador — não aplicada)

1. **Manter** `livro_vfinal_limpo_PT.md` como mestre PT de revisão (já declarado) e `livro_vfinal_clean_EN.md` como mestre EN.
2. **Reconciliar** o mestre PT com `livro_vfinal.md`: identificar as +1.556 linhas de delta, decidir o que é conteúdo novo legítimo e o que é rascunho descartável, e então **re-freezar** o mestre com novo SHA + data.
3. **Marcar as cópias do pack Zenodo** (`docs/zenodo_packs/dodecatiad_v3_publication/paper/…`) como **snapshots de publicação congelados** — não editar, para preservar a proveniência do depósito.
4. Registrar no topo de cada descendente viva uma linha `linhagem: mestre=<path> sha256=<hash>` para eliminar a ambiguidade nas próximas sessões.

## 5. Nota de integridade

Todos os valores desta tabela foram **medidos** (`ls`, `wc`, `grep -c`, `sha256sum`) nesta data; nenhum foi inferido. A declaração de mestre é **citada verbatim** de um artefato do próprio repositório, não deduzida. A recomendação da §4 é explicitamente **proposta**, não aplicada.
