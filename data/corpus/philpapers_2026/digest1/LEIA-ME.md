# digest1 — BIBLIO-1 (PhilPapers)

- `manifest.json` — 303 itens do digest, com `n, titulo, autor, ano, venue, score (0-3), status_download, path_ou_url` (+ `doi`, `oa_source`, `kw_principais`).
- PDFs nomeados `NNN_autor_ano_titulocurto.pdf` (NNN = número do item no digest).

## status_download
| valor | significado |
|---|---|
| `baixado` | PDF open-access validado (`%PDF` + 1.ª página conferida contra o título) |
| `paywall` | DOI existe, sem versão OA (ver `doi` no manifest para acesso institucional) |
| `philarchive_bloqueado_cloudflare403` | URL `philpapers.org/archive/*.pdf` localizado mas bloqueado por Cloudflare neste host |
| `sem_oa_localizado` | sem DOI e sem URL OA (em regra preprints só em PhilArchive) |
| `nao_priorizado_score<2` | item fora do alvo (score 0-1); download não tentado |

Sem qualquer acesso pago. Relatório: `/var/omnimind_storage/home_redirect/reports_runtime/biblio_digest1_20261005.md`.
